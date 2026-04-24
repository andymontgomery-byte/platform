CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS registry;
CREATE SCHEMA IF NOT EXISTS dictionary;

CREATE TABLE IF NOT EXISTS registry.standard_families (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  family_key text NOT NULL UNIQUE,
  name text NOT NULL,
  plain_description text NOT NULL,
  platform_posture text NOT NULL CHECK (platform_posture IN ('lead', 'prepare', 'support', 'legacy', 'governance')),
  platform_role text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE registry.standard_families IS
  'A 1EdTech standard family or related practice area that the platform tracks.';
COMMENT ON COLUMN registry.standard_families.family_key IS
  'Stable lowercase key used in dictionary references, for example oneroster or qti.';
COMMENT ON COLUMN registry.standard_families.plain_description IS
  'School-friendly explanation of what this standard family is for.';
COMMENT ON COLUMN registry.standard_families.platform_posture IS
  'Whether the platform leads with, prepares for, supports, treats as legacy, or uses this standard for governance.';

CREATE TABLE IF NOT EXISTS registry.standard_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  family_id uuid NOT NULL REFERENCES registry.standard_families(id) ON DELETE CASCADE,
  version_label text NOT NULL,
  release_status text NOT NULL,
  release_date date,
  latest_public_version boolean NOT NULL DEFAULT false,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (family_id, version_label)
);

COMMENT ON TABLE registry.standard_versions IS
  'Specific standard versions, statuses, and release dates tracked by the platform.';
COMMENT ON COLUMN registry.standard_versions.version_label IS
  'Version label from the standard publisher, for example 1.2, 3.0, or Candidate Final Public.';
COMMENT ON COLUMN registry.standard_versions.release_status IS
  'Publisher status such as Final, Candidate Final, Public Draft, framework, rubric, or legacy.';

CREATE TABLE IF NOT EXISTS registry.standard_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  standard_version_id uuid REFERENCES registry.standard_versions(id) ON DELETE CASCADE,
  family_id uuid REFERENCES registry.standard_families(id) ON DELETE CASCADE,
  title text NOT NULL,
  url text NOT NULL,
  source_type text NOT NULL CHECK (source_type IN ('overview', 'specification', 'binding', 'implementation_guide', 'certification', 'announcement', 'rubric', 'validator', 'other')),
  retrieved_on date NOT NULL,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (standard_version_id IS NOT NULL OR family_id IS NOT NULL)
);

COMMENT ON TABLE registry.standard_sources IS
  'Official source links used to understand a standard family or version.';
COMMENT ON COLUMN registry.standard_sources.retrieved_on IS
  'Date we checked the source, so later reviews know how fresh the research is.';

CREATE TABLE IF NOT EXISTS dictionary.privacy_classes (
  privacy_class text PRIMARY KEY,
  plain_description text NOT NULL,
  handling_notes text NOT NULL
);

COMMENT ON TABLE dictionary.privacy_classes IS
  'Plain-language privacy categories used by all dictionary fields.';

CREATE TABLE IF NOT EXISTS dictionary.data_domains (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_key text NOT NULL UNIQUE,
  name text NOT NULL,
  plain_description text NOT NULL,
  primary_standard_family_id uuid REFERENCES registry.standard_families(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE dictionary.data_domains IS
  'Major areas of platform data, such as roster, assessment, standards, learning activity, or credentials.';

CREATE TABLE IF NOT EXISTS dictionary.objects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_id uuid NOT NULL REFERENCES dictionary.data_domains(id),
  object_key text NOT NULL UNIQUE,
  name text NOT NULL,
  object_type text NOT NULL CHECK (object_type IN ('storage_table', 'sql_view', 'api_resource', 'event', 'file_record', 'package', 'concept')),
  plain_description text NOT NULL,
  why_it_exists text NOT NULL,
  source_standard_family_id uuid REFERENCES registry.standard_families(id),
  source_standard_version_id uuid REFERENCES registry.standard_versions(id),
  privacy_class text NOT NULL REFERENCES dictionary.privacy_classes(privacy_class),
  lifecycle_status text NOT NULL DEFAULT 'proposed' CHECK (lifecycle_status IN ('proposed', 'active', 'deprecated', 'removed')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE dictionary.objects IS
  'Documented platform objects exposed through SQL, APIs, events, files, packages, or conceptual docs.';
COMMENT ON COLUMN dictionary.objects.object_key IS
  'Stable object key used by API docs, SQL docs, and field references.';
COMMENT ON COLUMN dictionary.objects.plain_description IS
  'School-friendly explanation of what this object represents.';
COMMENT ON COLUMN dictionary.objects.why_it_exists IS
  'Reason this object is part of the platform, stated in product terms.';

CREATE TABLE IF NOT EXISTS dictionary.fields (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  object_id uuid NOT NULL REFERENCES dictionary.objects(id) ON DELETE CASCADE,
  field_key text NOT NULL,
  name text NOT NULL,
  technical_name text NOT NULL,
  data_type text NOT NULL,
  required boolean NOT NULL DEFAULT false,
  plain_description text NOT NULL,
  school_example text,
  allowed_values_summary text,
  source_standard_family_id uuid REFERENCES registry.standard_families(id),
  source_standard_version_id uuid REFERENCES registry.standard_versions(id),
  privacy_class text NOT NULL REFERENCES dictionary.privacy_classes(privacy_class),
  access_notes text NOT NULL,
  common_mistakes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (object_id, field_key)
);

COMMENT ON TABLE dictionary.fields IS
  'Documented fields for platform objects, including meaning, type, examples, privacy class, access notes, and source standard.';
COMMENT ON COLUMN dictionary.fields.field_key IS
  'Stable field key within the object, usually matching the JSON or SQL field name.';
COMMENT ON COLUMN dictionary.fields.school_example IS
  'Concrete example that helps a school-experienced reader understand the field.';
COMMENT ON COLUMN dictionary.fields.common_mistakes IS
  'Short warning about common integration or interpretation errors.';

CREATE TABLE IF NOT EXISTS dictionary.enum_values (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id uuid NOT NULL REFERENCES dictionary.fields(id) ON DELETE CASCADE,
  value text NOT NULL,
  label text NOT NULL,
  plain_description text NOT NULL,
  source_standard_value text,
  sort_order integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (field_id, value)
);

COMMENT ON TABLE dictionary.enum_values IS
  'Allowed values for fields that use a controlled vocabulary.';

CREATE TABLE IF NOT EXISTS dictionary.relationships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  relationship_key text NOT NULL UNIQUE,
  from_object_id uuid NOT NULL REFERENCES dictionary.objects(id) ON DELETE CASCADE,
  to_object_id uuid NOT NULL REFERENCES dictionary.objects(id) ON DELETE CASCADE,
  relationship_type text NOT NULL CHECK (relationship_type IN ('belongs_to', 'has_many', 'many_to_many', 'references', 'aligns_to', 'derived_from', 'same_as')),
  plain_description text NOT NULL,
  cardinality text NOT NULL,
  required boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE dictionary.relationships IS
  'Plain-language relationship map between documented platform objects.';

CREATE TABLE IF NOT EXISTS dictionary.sql_surfaces (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  object_id uuid NOT NULL REFERENCES dictionary.objects(id) ON DELETE CASCADE,
  schema_name text NOT NULL,
  relation_name text NOT NULL,
  relation_type text NOT NULL CHECK (relation_type IN ('table', 'view', 'materialized_view')),
  stability text NOT NULL CHECK (stability IN ('internal', 'public_contract', 'standard_projection')),
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (schema_name, relation_name)
);

COMMENT ON TABLE dictionary.sql_surfaces IS
  'SQL tables and views that expose documented objects.';

CREATE TABLE IF NOT EXISTS dictionary.api_resources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  object_id uuid REFERENCES dictionary.objects(id) ON DELETE SET NULL,
  resource_key text NOT NULL UNIQUE,
  path_template text NOT NULL,
  method text NOT NULL CHECK (method IN ('GET', 'POST', 'PUT', 'PATCH', 'DELETE')),
  plain_description text NOT NULL,
  required_scope text,
  lifecycle_status text NOT NULL DEFAULT 'proposed' CHECK (lifecycle_status IN ('proposed', 'active', 'deprecated', 'removed')),
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE dictionary.api_resources IS
  'API endpoints generated or documented from the same data dictionary as SQL surfaces.';

CREATE TABLE IF NOT EXISTS dictionary.api_field_mappings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  field_id uuid NOT NULL REFERENCES dictionary.fields(id) ON DELETE CASCADE,
  api_resource_id uuid NOT NULL REFERENCES dictionary.api_resources(id) ON DELETE CASCADE,
  json_path text NOT NULL,
  required_in_response boolean NOT NULL DEFAULT false,
  required_in_request boolean NOT NULL DEFAULT false,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (api_resource_id, json_path)
);

COMMENT ON TABLE dictionary.api_field_mappings IS
  'Mapping from dictionary fields to JSON paths in API requests and responses.';

CREATE TABLE IF NOT EXISTS dictionary.change_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  changed_at timestamptz NOT NULL DEFAULT now(),
  changed_by text NOT NULL,
  change_type text NOT NULL CHECK (change_type IN ('add', 'update', 'deprecate', 'remove', 'rename')),
  target_type text NOT NULL CHECK (target_type IN ('standard', 'domain', 'object', 'field', 'enum', 'relationship', 'api_resource', 'sql_surface')),
  target_key text NOT NULL,
  plain_summary text NOT NULL
);

COMMENT ON TABLE dictionary.change_log IS
  'Audit trail for changes to standards registry and dictionary metadata.';
