import { createClient } from "@supabase/supabase-js";

// decision_id: DEC-015-service-role-policy; caller Authorization is forwarded so RLS applies.
// decision_id: DEC-013-audit-response-truth; the audit block is built from audit_log rows read back by request_id.
// decision_id: DEC-011-privacy-surfaces; directory fields are only returned through an audited user-JWT path.

type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
type JsonObject = { [key: string]: JsonValue };

type AuditedPersonRow = {
  id: string;
  sourced_id: string;
  display_name: string;
  given_name: string | null;
  family_name: string | null;
  email: string | null;
  primary_role: string;
};

type AuditLogRow = {
  id: number;
  field_accessed: string;
  client_id: string;
  scope: string;
  purpose: string;
  tenant_id: string;
  request_id: string | null;
  timestamp: string;
};

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
  "access-control-allow-methods": "GET, OPTIONS",
};

Deno.serve(async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "GET") {
    return json({ error: "method_not_allowed", message: "Use GET for audited roster reads." }, 405);
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

  const clientId = readClaim(jwt, "client_id", "azp") ||
    readNestedClaim(jwt, "app_metadata", "client_id") ||
    readHeader(req, "x-platform-client-id");
  const scope = readScope(jwt) || readHeader(req, "x-platform-scope");
  const purpose = readClaim(jwt, "purpose") ||
    readNestedClaim(jwt, "app_metadata", "purpose") ||
    readHeader(req, "x-platform-purpose");

  const missing = [
    ["client_id", clientId],
    ["scope", scope],
    ["purpose", purpose],
  ].filter(([, value]) => !value).map(([name]) => name);
  if (missing.length) {
    return json({
      error: "missing_audit_claims",
      message: `Audited sensitive reads require ${missing.join(", ")}.`,
    }, 403);
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY") || Deno.env.get("SUPABASE_PUBLISHABLE_KEY");
  if (!supabaseUrl || !supabaseAnonKey) {
    return json({ error: "server_misconfigured", message: "Supabase URL or public API key is missing." }, 500);
  }

  const url = new URL(req.url);
  const personId = (url.searchParams.get("personId") || "person_ada").trim();
  if (!personId || personId.length > 128) {
    return json({ error: "invalid_person_id", message: "personId must be 1 to 128 characters." }, 400);
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
  const { data, error } = await supabase.rpc("read_people_sensitive_audited", {
    person_id: personId,
    client_id: clientId,
    scope,
    purpose,
    request_path: url.pathname,
    request_id: requestId,
  });

  if (error) {
    return json({ error: "audited_read_failed", message: error.message }, 400);
  }

  const rows = Array.isArray(data) ? data as AuditedPersonRow[] : [];
  if (rows.length === 0) {
    return json({ error: "not_found", message: "No visible person matched the requested id." }, 404);
  }

  const person = rows[0];
  const { data: auditData, error: auditError } = await supabase
    .from("audit_log")
    .select("id,field_accessed,client_id,scope,purpose,tenant_id,request_id,timestamp")
    .eq("request_id", requestId)
    .eq("subject_table", "people")
    .eq("subject_id", person.id)
    .eq("client_id", clientId)
    .eq("scope", scope)
    .eq("purpose", purpose)
    .eq("tenant_id", tenantId)
    .order("id", { ascending: true });

  if (auditError) {
    return json({ error: "audit_confirmation_failed", message: auditError.message }, 500);
  }

  const auditRows = Array.isArray(auditData) ? auditData as AuditLogRow[] : [];
  if (auditRows.length === 0) {
    return json({
      error: "audit_confirmation_failed",
      message: "The audited read completed, but no matching audit_log rows were visible for this request.",
    }, 500);
  }

  return json({
    person: {
      id: person.id,
      sourcedId: person.sourced_id,
      displayName: person.display_name,
      givenName: person.given_name,
      familyName: person.family_name,
      email: person.email,
      primaryRole: person.primary_role,
    },
    audit: {
      logged: auditRows.length,
      fields: auditRows.map((row) => row.field_accessed),
      clientId: auditRows[0].client_id,
      scope: auditRows[0].scope,
      purpose: auditRows[0].purpose,
      tenantId: auditRows[0].tenant_id,
      requestId: auditRows[0].request_id,
      confirmedAt: auditRows[auditRows.length - 1].timestamp,
    },
  });
});

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

function readScope(jwt: JsonObject | null): string | null {
  const direct = readScopeValue(jwt?.scope ?? jwt?.scp);
  if (direct) {
    return direct;
  }
  const appMetadata = jwt?.app_metadata;
  if (isObject(appMetadata)) {
    return readScopeValue(appMetadata.scope ?? appMetadata.scp);
  }
  return null;
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
