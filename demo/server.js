import Database from "better-sqlite3";
import express from "express";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const dictionary = JSON.parse(
  fs.readFileSync(path.join(root, "dictionary", "oneroster-core.v1.json"), "utf8")
);
const db = new Database(path.join(__dirname, "platform-demo.sqlite"), {
  readonly: true,
  fileMustExist: true
});

const app = express();
const port = Number(process.env.PORT || 8787);

app.use(express.json({ limit: "64kb" }));
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  if (req.method === "OPTIONS") {
    res.sendStatus(204);
    return;
  }
  next();
});

const objects = new Map(dictionary.objects.map((object) => [object.api_path, object]));
const objectsByKey = new Map(dictionary.objects.map((object) => [object.object_key, object]));
const personObject = objectsByKey.get("person");

app.get("/health", (req, res) => {
  res.json({
    ok: true,
    name: "Platform OneRoster Core Demo API",
    dictionaryVersion: dictionary.dictionary_version
  });
});

app.get("/dictionary", (req, res) => {
  res.json(dictionary);
});

app.get("/dictionary/objects", (req, res) => {
  res.json({
    items: dictionary.objects.map((object) => ({
      objectKey: object.object_key,
      tableName: object.table_name,
      apiPath: object.api_path,
      name: object.name,
      plainDescription: object.plain_description,
      privacyClass: object.privacy_class
    })),
    count: dictionary.objects.length
  });
});

app.get("/dictionary/objects/:objectKey", (req, res) => {
  const object = objectsByKey.get(req.params.objectKey);
  if (!object) {
    res.status(404).json({ error: "Object not found" });
    return;
  }
  res.json(toCamelObject(object));
});

for (const object of objects.values()) {
  if (object.object_key === "person") {
    continue;
  }

  app.get(object.api_path, (req, res) => {
    const rows = listRows(object, req.query.q);
    res.json({ items: rows.map((row) => rowToJson(object, row)), count: rows.length });
  });

  app.get(`${object.api_path}/:id`, (req, res) => {
    const row = db.prepare(`select * from ${object.table_name} where id = ?`).get(req.params.id);
    if (!row) {
      res.status(404).json({ error: `${object.name} not found` });
      return;
    }
    res.json(rowToJson(object, row));
  });
}

if (personObject) {
  app.get("/users", (req, res) => {
    const rows = listRows(personObject, req.query.q);
    res.json({ users: rows.map(rowToOneRosterUser) });
  });

  app.get("/users/:sourcedId", (req, res) => {
    const row = db.prepare("select * from people where sourced_id = ?").get(req.params.sourcedId);
    if (!row) {
      res.status(404).json({ error: "User not found" });
      return;
    }
    res.json({ user: rowToOneRosterUser(row) });
  });
}

app.get("/views/class-roster", (req, res) => {
  const rows = db.prepare("select * from class_roster order by class_title, class_role, display_name").all();
  res.json({ items: rows, count: rows.length });
});

app.get("/views/gradebook-results", (req, res) => {
  const rows = db.prepare("select * from gradebook_results order by class_title, line_item_title, learner_name").all();
  res.json({ items: rows, count: rows.length });
});

app.post("/sql/query", (req, res) => {
  const sql = String(req.body?.sql || "").trim();
  if (!isReadOnlySql(sql)) {
    res.status(400).json({
      error: "Only one read-only SELECT or WITH query is allowed.",
      example: "select display_name, primary_role from people order by display_name"
    });
    return;
  }

  try {
    const statement = db.prepare(sql);
    if (!statement.reader) {
      res.status(400).json({ error: "Query must return rows." });
      return;
    }
    const rows = statement.all();
    const columns = rows.length ? Object.keys(rows[0]) : statement.columns().map((column) => column.name);
    res.json({ columns, rows, count: rows.length });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

app.listen(port, () => {
  console.log(`Platform OneRoster Core Demo API listening on http://localhost:${port}`);
});

function listRows(object, query) {
  const fields = object.fields.map((field) => field.column_name);
  const searchFields = fields.filter((field) =>
    ["name", "title", "display_name", "email", "sourced_id", "course_code", "class_code"].includes(field)
  );

  if (query && searchFields.length) {
    const where = searchFields.map((field) => `${field} like ?`).join(" or ");
    const params = searchFields.map(() => `%${query}%`);
    return db
      .prepare(`select * from ${object.table_name} where ${where} order by id`)
      .all(params);
  }

  return db.prepare(`select * from ${object.table_name} order by id`).all();
}

function rowToJson(object, row) {
  const output = {};
  for (const field of object.fields) {
    output[field.json_name] = row[field.column_name] ?? null;
  }
  return output;
}

function rowToOneRosterUser(row) {
  return removeNullValues({
    sourcedId: row.sourced_id,
    status: row.status,
    dateLastModified: row.date_last_modified,
    enabledUser: row.enabled_user === "true",
    givenName: row.given_name,
    familyName: row.family_name,
    email: row.email,
    roles: [
      {
        roleType: "primary",
        role: row.primary_role
      }
    ],
    metadata: {
      platformId: row.id,
      displayName: row.display_name
    }
  });
}

function removeNullValues(value) {
  if (Array.isArray(value)) {
    return value.map(removeNullValues);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, entry]) => entry !== null && entry !== undefined)
        .map(([key, entry]) => [key, removeNullValues(entry)])
    );
  }
  return value;
}

function toCamelObject(value) {
  if (Array.isArray(value)) {
    return value.map(toCamelObject);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, entry]) => [toCamelKey(key), toCamelObject(entry)])
    );
  }
  return value;
}

function toCamelKey(value) {
  return value.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

function isReadOnlySql(sql) {
  if (!sql) {
    return false;
  }
  const withoutComments = sql
    .replace(/--.*$/gm, "")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .trim();
  if (!/^(select|with)\b/i.test(withoutComments)) {
    return false;
  }
  if (withoutComments.split(";").filter((part) => part.trim()).length > 1) {
    return false;
  }
  return !/\b(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|pragma|vacuum|reindex)\b/i.test(
    withoutComments
  );
}
