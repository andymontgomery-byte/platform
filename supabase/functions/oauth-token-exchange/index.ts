import { createClient } from "@supabase/supabase-js";

// decision_id: DEC-015-service-role-policy; caller Authorization is forwarded so RLS applies.
// decision_id: DEC-012-runtime-coverage-per-spec; this is the partial Security Framework runtime receipt path.

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

const supportedGrantTypes = new Set([
  "authorization_code",
  "client_credentials",
  "refresh_token",
  "urn:ietf:params:oauth:grant-type:token-exchange",
]);

Deno.serve(async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return json({ error: "method_not_allowed", message: "Use POST for OAuth token exchange." }, 405);
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

  const body = await readBody(req);
  if (body instanceof Response) {
    return body;
  }

  const grantType = readString(body.grant_type ?? body.grantType);
  const clientId = readString(body.client_id ?? body.clientId) ||
    readClaim(jwt, "client_id", "azp") ||
    readNestedClaim(jwt, "app_metadata", "client_id");
  const requestedScope = readString(body.scope) || readScope(jwt, req);

  const missing = [
    ["grant_type", grantType],
    ["client_id", clientId],
    ["scope", requestedScope],
  ].filter(([, value]) => !value).map(([name]) => name);
  if (missing.length) {
    return json({ error: "invalid_token_request", message: `Missing required fields: ${missing.join(", ")}.` }, 400);
  }

  if (!supportedGrantTypes.has(grantType)) {
    return json({ error: "unsupported_grant_type", message: `Unsupported grant_type '${grantType}'.` }, 400);
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

  const audit = await supabase
    .from("audit_log")
    .insert({
      tenant_id: tenantId,
      client_id: clientId,
      scope: requestedScope,
      purpose: readPurpose(jwt, req) || "oauth-token-exchange",
      field_accessed: `oauth.token_exchange.${grantType}`,
      subject_table: "oauth_token_exchange",
      subject_id: clientId,
      request_path: new URL(req.url).pathname,
      request_id: readHeader(req, "x-request-id") || crypto.randomUUID(),
    })
    .select("id,timestamp")
    .single();

  if (audit.error) {
    return json({ error: "token_exchange_audit_failed", message: audit.error.message }, 400);
  }

  return json({
    token_type: "Bearer",
    expires_in: 300,
    scope: requestedScope,
    access_token: authorization.replace(/^bearer\s+/i, ""),
    platform_token_use: "sandbox-user-jwt-exchange",
    audit: {
      id: audit.data.id,
      timestamp: audit.data.timestamp,
    },
  });
});

async function readBody(req: Request): Promise<JsonObject | Response> {
  const contentType = req.headers.get("content-type") || "";
  if (contentType.includes("application/x-www-form-urlencoded")) {
    const params = new URLSearchParams(await req.text());
    const body: JsonObject = {};
    for (const [key, value] of params.entries()) {
      body[key] = value;
    }
    return body;
  }

  try {
    const payload = await req.json();
    return isObject(payload)
      ? payload
      : json({ error: "invalid_json", message: "Request body must be a JSON object." }, 400);
  } catch {
    return json({ error: "invalid_json", message: "Request body must be valid JSON or form-encoded data." }, 400);
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
