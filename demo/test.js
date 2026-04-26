import assert from "node:assert/strict";
import { spawn } from "node:child_process";

const port = 8791;
const server = spawn(process.execPath, ["server.js"], {
  cwd: new URL(".", import.meta.url),
  env: { ...process.env, PORT: String(port) },
  stdio: ["ignore", "pipe", "pipe"]
});

try {
  await waitForHealth(port);

  const organizations = await getJson(port, "/organizations");
  assert.equal(organizations.count, 3);
  assert.equal(organizations.items[0].sourcedId !== undefined, true);

  const users = await getJson(port, "/users?q=Ada");
  assert.equal(Array.isArray(users.users), true);
  assert.equal(users.users[0].sourcedId, "USER-ADA");
  assert.equal(Object.hasOwn(users.users[0], "id"), false);

  const user = await getJson(port, "/users/USER-ADA");
  assert.equal(user.user.sourcedId, "USER-ADA");
  assert.equal(user.user.metadata.platformId, "person_ada");
  assert.equal(Object.hasOwn(user.user, "id"), false);

  const localIdLookup = await getJson(port, "/users/person_ada", 404);
  assert.match(localIdLookup.error, /not found/i);

  const nativePeopleRoute = await getJson(port, "/people/person_ada", 404);
  assert.match(nativePeopleRoute.error, /route not found/i);

  const roster = await getJson(port, "/views/class-roster");
  assert.equal(roster.items.some((row) => row.display_name === "Ada Johnson"), true);

  const sql = await postJson(port, "/sql/query", {
    sql: "select display_name, primary_role from people order by display_name"
  });
  assert.equal(sql.columns.includes("display_name"), true);
  assert.equal(sql.count, 6);

  const blocked = await postJson(port, "/sql/query", {
    sql: "delete from people"
  }, 400);
  assert.match(blocked.error, /read-only/i);

  console.log("demo-api-ok");
} finally {
  server.kill("SIGTERM");
}

async function waitForHealth(portNumber) {
  const deadline = Date.now() + 5000;
  while (Date.now() < deadline) {
    try {
      const health = await getJson(portNumber, "/health");
      if (health.ok) {
        return;
      }
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  throw new Error("Timed out waiting for demo API health");
}

async function getJson(portNumber, path, expectedStatus = 200) {
  const response = await fetch(`http://localhost:${portNumber}${path}`);
  assert.equal(response.status, expectedStatus, `${path} returned ${response.status}`);
  return response.json();
}

async function postJson(portNumber, path, body, expectedStatus = 200) {
  const response = await fetch(`http://localhost:${portNumber}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });
  assert.equal(response.status, expectedStatus, `${path} returned ${response.status}`);
  return response.json();
}
