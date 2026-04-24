import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const databasePath = path.join(__dirname, "platform-demo.sqlite");
const schemaPath = path.join(__dirname, "schema.sql");
const seedPath = path.join(__dirname, "seed.sql");

if (fs.existsSync(databasePath)) {
  fs.rmSync(databasePath);
}

const db = new Database(databasePath);
db.pragma("foreign_keys = ON");
db.exec(fs.readFileSync(schemaPath, "utf8"));
db.exec(fs.readFileSync(seedPath, "utf8"));

const tables = [
  "organizations",
  "people",
  "academic_sessions",
  "courses",
  "classes",
  "enrollments",
  "line_items",
  "results",
  "source_identifiers"
];

const counts = Object.fromEntries(
  tables.map((table) => [
    table,
    db.prepare(`select count(*) as count from ${table}`).get().count
  ])
);

db.close();
console.log(JSON.stringify({ databasePath, counts }, null, 2));
