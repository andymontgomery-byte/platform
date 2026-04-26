import { createClient } from "@supabase/supabase-js";

// decision_id: DEC-015-service-role-policy; caller Authorization is forwarded so RLS applies.
// decision_id: DEC-005-results-scores; gradebook writes use the platform result/score contract.
// decision_id: DEC-010-tenancy-reference-data; referenced rows must be visible in the caller tenant.

type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
type JsonObject = { [key: string]: JsonValue };

type RawSubmission = {
  id?: unknown;
  sourcedId?: unknown;
  sourced_id?: unknown;
  lineItemId?: unknown;
  line_item_id?: unknown;
  personId?: unknown;
  person_id?: unknown;
  scoreStatus?: unknown;
  score_status?: unknown;
  score?: unknown;
  scoreDate?: unknown;
  score_date?: unknown;
  comment?: unknown;
};

type ResultRow = {
  tenant_id: string;
  id: string;
  sourced_id: string;
  line_item_id: string;
  person_id: string;
  score_status: string;
  score: number | null;
  score_date: string | null;
  comment: string | null;
  status: "active";
  date_last_modified: string;
};

const corsHeaders = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "authorization, x-client-info, apikey, content-type, x-platform-purpose",
  "access-control-allow-methods": "POST, OPTIONS",
};

const validScoreStatuses = new Set(["notSubmitted", "submitted", "partiallyGraded", "fullyGraded"]);

Deno.serve(async (req: Request): Promise<Response> => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return json({ error: "method_not_allowed", message: "Use POST for gradebook bulk submit." }, 405);
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

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY") || Deno.env.get("SUPABASE_PUBLISHABLE_KEY");
  if (!supabaseUrl || !supabaseAnonKey) {
    return json({ error: "server_misconfigured", message: "Supabase URL or public API key is missing." }, 500);
  }

  let payload: unknown;
  try {
    payload = await req.json();
  } catch {
    return json({ error: "invalid_json", message: "Request body must be JSON." }, 400);
  }

  const submissions = readSubmissions(payload);
  if (submissions instanceof Response) {
    return submissions;
  }

  const now = new Date().toISOString();
  const rows: ResultRow[] = [];
  for (const [index, submission] of submissions.entries()) {
    const normalized = normalizeSubmission(submission, tenantId, now, index);
    if (normalized instanceof Response) {
      return normalized;
    }
    rows.push(normalized);
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

  const accessCheck = await validateTenantVisibleReferences(
    supabase,
    rows.map((row) => row.line_item_id),
    rows.map((row) => row.person_id),
  );
  if (accessCheck instanceof Response) {
    return accessCheck;
  }

  const { data, error } = await supabase
    .from("results")
    .upsert(rows, { onConflict: "id" })
    .select("id,sourced_id,line_item_id,person_id,score_status,score,score_date,comment,date_last_modified")
    .order("id", { ascending: true });

  if (error) {
    return json({ error: "gradebook_submit_failed", message: error.message }, 400);
  }

  return json({
    accepted: rows.length,
    results: (data || []).map((row) => ({
      id: row.id,
      sourcedId: row.sourced_id,
      lineItemId: row.line_item_id,
      personId: row.person_id,
      scoreStatus: row.score_status,
      score: row.score,
      scoreDate: row.score_date,
      comment: row.comment,
      dateLastModified: row.date_last_modified,
    })),
  });
});

function readSubmissions(payload: unknown): RawSubmission[] | Response {
  if (!isObject(payload)) {
    return json({ error: "invalid_payload", message: "Request body must be an object." }, 400);
  }
  const submissions = payload.submissions;
  if (!Array.isArray(submissions)) {
    return json({ error: "invalid_submissions", message: "Body must include a submissions array." }, 400);
  }
  if (submissions.length < 1 || submissions.length > 50) {
    return json({ error: "invalid_submission_count", message: "Submit between 1 and 50 results per request." }, 400);
  }
  if (!submissions.every(isObject)) {
    return json({ error: "invalid_submission", message: "Every submission must be an object." }, 400);
  }
  return submissions as RawSubmission[];
}

function normalizeSubmission(
  submission: RawSubmission,
  tenantId: string,
  now: string,
  index: number,
): ResultRow | Response {
  const id = readString(submission.id);
  const sourcedId = readString(submission.sourcedId ?? submission.sourced_id);
  const lineItemId = readString(submission.lineItemId ?? submission.line_item_id);
  const personId = readString(submission.personId ?? submission.person_id);
  const scoreStatus = readString(submission.scoreStatus ?? submission.score_status);

  const missing = [
    ["id", id],
    ["sourcedId", sourcedId],
    ["lineItemId", lineItemId],
    ["personId", personId],
    ["scoreStatus", scoreStatus],
  ]
    .filter(([, value]) => !value)
    .map(([field]) => field);
  if (missing.length) {
    return json({
      error: "invalid_submission",
      message: `Submission ${index} is missing required fields: ${missing.join(", ")}.`,
    }, 400);
  }

  if (!validScoreStatuses.has(scoreStatus)) {
    return json({
      error: "invalid_score_status",
      message: `Submission ${index} has unsupported scoreStatus '${scoreStatus}'.`,
    }, 400);
  }

  const score = readScore(submission.score);
  if (score instanceof Response) {
    return score;
  }

  const scoreDate = readOptionalDate(submission.scoreDate ?? submission.score_date);
  if (scoreDate instanceof Response) {
    return scoreDate;
  }

  const comment = readOptionalString(submission.comment);
  if (comment instanceof Response) {
    return comment;
  }

  return {
    tenant_id: tenantId,
    id,
    sourced_id: sourcedId,
    line_item_id: lineItemId,
    person_id: personId,
    score_status: scoreStatus,
    score,
    score_date: scoreDate,
    comment,
    status: "active",
    date_last_modified: now,
  };
}

async function validateTenantVisibleReferences(
  supabase: ReturnType<typeof createClient>,
  lineItemIds: string[],
  personIds: string[],
): Promise<true | Response> {
  const uniqueLineItemIds = unique(lineItemIds);
  const uniquePersonIds = unique(personIds);

  const lineItems = await supabase.from("line_items").select("id").in("id", uniqueLineItemIds);
  if (lineItems.error) {
    return json({ error: "line_item_check_failed", message: lineItems.error.message }, 400);
  }
  const visibleLineItems = new Set((lineItems.data || []).map((row) => row.id));
  const missingLineItems = uniqueLineItemIds.filter((id) => !visibleLineItems.has(id));
  if (missingLineItems.length) {
    return json({
      error: "line_item_not_visible",
      message: "One or more line items are not visible to the caller's tenant.",
      ids: missingLineItems,
    }, 403);
  }

  const people = await supabase.from("people").select("id").in("id", uniquePersonIds);
  if (people.error) {
    return json({ error: "person_check_failed", message: people.error.message }, 400);
  }
  const visiblePeople = new Set((people.data || []).map((row) => row.id));
  const missingPeople = uniquePersonIds.filter((id) => !visiblePeople.has(id));
  if (missingPeople.length) {
    return json({
      error: "person_not_visible",
      message: "One or more learners are not visible to the caller's tenant.",
      ids: missingPeople,
    }, 403);
  }

  return true;
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
  if (!jwt) {
    return null;
  }
  const direct = readString(jwt.tenant_id);
  if (direct) {
    return direct;
  }
  const appMetadata = jwt.app_metadata;
  if (isObject(appMetadata)) {
    return readString(appMetadata.tenant_id);
  }
  return null;
}

function readScore(value: unknown): number | null | Response {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return json({ error: "invalid_score", message: "score must be a finite number or null." }, 400);
  }
  return value;
}

function readOptionalDate(value: unknown): string | null | Response {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  const text = readString(value);
  if (!text || Number.isNaN(Date.parse(text))) {
    return json({ error: "invalid_score_date", message: "scoreDate must be an ISO date-time string." }, 400);
  }
  return new Date(text).toISOString();
}

function readOptionalString(value: unknown): string | null | Response {
  if (value === undefined || value === null) {
    return null;
  }
  const text = readString(value);
  if (!text) {
    return null;
  }
  if (text.length > 1000) {
    return json({ error: "invalid_comment", message: "comment must be 1000 characters or fewer." }, 400);
  }
  return text;
}

function readString(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function isObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function unique(values: string[]): string[] {
  return Array.from(new Set(values));
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
