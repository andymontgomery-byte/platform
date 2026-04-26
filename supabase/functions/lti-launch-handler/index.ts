import { createClient } from "@supabase/supabase-js";

type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
type JsonObject = { [key: string]: JsonValue };

const corsHeaders = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": [
    "authorization",
    "x-client-info",
    "apikey",
    "content-type",
    "x-platform-client-id",
    "x-platform-purpose",
    "x-platform-scope",
    "x-request-id",
  ].join(", "),
  "access-control-allow-methods": "POST, OPTIONS",
};

Deno.serve(async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return json({ error: "method_not_allowed", message: "Use POST for LTI launch handling." }, 405);
  }

  const authorization = req.headers.get("Authorization");
  if (!authorization || !authorization.toLowerCase().startsWith("bearer ")) {
    return json({ error: "missing_authorization", message: "A Supabase Auth bearer token is required." }, 401);
  }

  const jwt = decodeJwtPayload(authorization);
  const tenantId = readTenantId(jwt);
  if (!tenantId) {
    return json({ error: "missing_tenant", message: "The bearer token must carry a tenant_id claim." }, 403);
  }

  const payload = await readJsonObject(req);
  if (payload instanceof Response) {
    return payload;
  }

  const messageType = readString(payload.messageType ?? payload["https://purl.imsglobal.org/spec/lti/claim/message_type"]) ||
    "LtiResourceLinkRequest";
  const contextId = readString(payload.contextId ?? payload["https://purl.imsglobal.org/spec/lti/claim/context_id"]);
  const resourceLinkId = readString(
    payload.resourceLinkId ?? payload["https://purl.imsglobal.org/spec/lti/claim/resource_link_id"],
  );
  const userId = readString(payload.userId ?? payload.sub);

  const missing = [
    ["contextId", contextId],
    ["resourceLinkId", resourceLinkId],
    ["userId", userId],
  ].filter(([, value]) => !value).map(([name]) => name);
  if (missing.length) {
    return json({ error: "invalid_launch", message: `Missing required LTI launch fields: ${missing.join(", ")}.` }, 400);
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY") || Deno.env.get("SUPABASE_PUBLISHABLE_KEY");
  if (!supabaseUrl || !supabaseAnonKey) {
    return json({ error: "server_misconfigured", message: "Supabase URL or public API key is missing." }, 500);
  }

  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
    global: {
      headers: {
        Authorization: authorization,
      },
    },
  });

  const context = await supabase
    .from("source_identifiers")
    .select("object_id,object_type,external_id")
    .eq("identifier_type", "ltiContextId")
    .eq("external_id", contextId)
    .maybeSingle();

  if (context.error) {
    return json({ error: "context_lookup_failed", message: context.error.message }, 400);
  }
  if (!context.data) {
    return json({
      error: "context_not_visible",
      message: "No tenant-visible class context matched the LTI context identifier.",
    }, 404);
  }

  const audit = await supabase
    .from("audit_log")
    .insert({
      tenant_id: tenantId,
      client_id: readClientId(jwt, req, payload),
      scope: readScope(jwt, req) || "platform.lti.launch",
      purpose: readPurpose(jwt, req) || "lti-launch",
      field_accessed: "lti.launch.context",
      subject_table: "source_identifiers",
      subject_id: context.data.external_id,
      request_path: new URL(req.url).pathname,
      request_id: readHeader(req, "x-request-id") || crypto.randomUUID(),
    })
    .select("id,timestamp")
    .single();

  if (audit.error) {
    return json({ error: "launch_audit_failed", message: audit.error.message }, 400);
  }

  return json({
    accepted: true,
    launch: {
      messageType,
      contextId,
      resourceLinkId,
      userId,
      tenantId,
    },
    rosterContext: {
      objectType: context.data.object_type,
      objectId: context.data.object_id,
    },
    audit: {
      id: audit.data.id,
      timestamp: audit.data.timestamp,
    },
  });
});

async function readJsonObject(req: Request): Promise<JsonObject | Response> {
  try {
    const payload = await req.json();
    return isObject(payload)
      ? payload
      : json({ error: "invalid_json", message: "Request body must be a JSON object." }, 400);
  } catch {
    return json({ error: "invalid_json", message: "Request body must be valid JSON." }, 400);
  }
}

function decodeJwtPayload(authorization: string): JsonObject | null {
  const token = authorization.replace(/^bearer\s+/i, "");
  const parts = token.split(".");
  if (parts.length < 2) {
    return null;
  }
  try {
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
    const decoded = JSON.parse(atob(padded));
    return isObject(decoded) ? decoded : null;
  } catch {
    return null;
  }
}

function readTenantId(jwt: JsonObject | null): string | null {
  return readClaim(jwt, "tenant_id") || readNestedClaim(jwt, "app_metadata", "tenant_id");
}

function readClientId(jwt: JsonObject | null, req: Request, payload: JsonObject): string {
  return readClaim(jwt, "client_id", "azp") ||
    readNestedClaim(jwt, "app_metadata", "client_id") ||
    readHeader(req, "x-platform-client-id") ||
    readString(payload.clientId ?? payload.client_id) ||
    "demo-lti-client";
}

function readScope(jwt: JsonObject | null, req: Request): string | null {
  const appMetadata = jwt?.app_metadata;
  return readScopeValue(jwt?.scope ?? jwt?.scp) ||
    readScopeValue(isObject(appMetadata) ? appMetadata.scope ?? appMetadata.scp : null) ||
    readHeader(req, "x-platform-scope");
}

function readPurpose(jwt: JsonObject | null, req: Request): string | null {
  return readClaim(jwt, "purpose") ||
    readNestedClaim(jwt, "app_metadata", "purpose") ||
    readHeader(req, "x-platform-purpose");
}

function readScopeValue(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }
  if (Array.isArray(value)) {
    const scopes = value.filter((item): item is string => typeof item === "string" && item.trim());
    return scopes.length ? scopes.map((item) => item.trim()).join(" ") : null;
  }
  return null;
}

function readClaim(jwt: JsonObject | null, ...keys: string[]): string | null {
  if (!jwt) {
    return null;
  }
  for (const key of keys) {
    const value = jwt[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }
  return null;
}

function readNestedClaim(jwt: JsonObject | null, parentKey: string, childKey: string): string | null {
  const parent = jwt?.[parentKey];
  if (!isObject(parent)) {
    return null;
  }
  const value = parent[childKey];
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function readString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function readHeader(req: Request, name: string): string | null {
  const value = req.headers.get(name);
  return value && value.trim() ? value.trim() : null;
}

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function json(body: JsonValue, status = 200): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      "content-type": "application/json; charset=utf-8",
    },
  });
}
