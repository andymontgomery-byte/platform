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
    return json({ error: "method_not_allowed", message: "Use POST for Caliper event ingestion." }, 405);
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

  const events = readCaliperEvents(payload);
  if (events instanceof Response) {
    return events;
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

  const requestId = readHeader(req, "x-request-id") || crypto.randomUUID();
  const rows = events.map((event, index) => {
    const eventType = readString(event.type ?? event["@type"] ?? event.eventType) || "CaliperEvent";
    const eventId = readString(event.id ?? event["@id"]) || `${requestId}:${index + 1}`;
    return {
      tenant_id: tenantId,
      client_id: readClientId(jwt, req, payload),
      scope: readScope(jwt, req) || "platform.caliper.events:write",
      purpose: readPurpose(jwt, req) || "learning-analytics",
      field_accessed: `caliper.event.${eventType}`,
      subject_table: "caliper_event",
      subject_id: eventId,
      request_path: new URL(req.url).pathname,
      request_id: requestId,
    };
  });

  const { data, error } = await supabase
    .from("audit_log")
    .insert(rows)
    .select("id,timestamp,field_accessed,subject_id")
    .order("id", { ascending: true });

  if (error) {
    return json({ error: "caliper_ingest_failed", message: error.message }, 400);
  }

  return json({
    accepted: events.length,
    tenantId,
    receipts: data || [],
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

function readCaliperEvents(payload: JsonObject): JsonObject[] | Response {
  const rawData = payload.data;
  const rawEvents = Array.isArray(rawData) ? rawData : [payload];
  const events = rawEvents.filter(isObject);
  if (events.length !== rawEvents.length) {
    return json({ error: "invalid_events", message: "Each Caliper event must be a JSON object." }, 400);
  }
  if (events.length < 1 || events.length > 25) {
    return json({ error: "invalid_event_count", message: "Submit between 1 and 25 Caliper events per request." }, 400);
  }
  return events;
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
    "demo-caliper-sensor";
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
