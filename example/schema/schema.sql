CREATE TABLE sample (
	id STRING(64) NOT NULL,
	address STRING(MAX),
	is_active BOOL NOT NULL,
	join_date DATE,
	modified_at TIMESTAMP OPTIONS (allow_commit_timestamp=true),
	name STRING(100) NOT NULL,
	points INT64 NOT NULL,
) PRIMARY KEY (id)

CREATE TABLE users (
    id STRING(MAX) NOT NULL,
    acl STRING(MAX),
    created_at TIMESTAMP,
    created_by STRING(MAX),
    email STRING(MAX),
    is_deleted BOOL,
    name STRING(MAX),
    organization_id STRING(MAX),
    password STRING(MAX),
    phone_number STRING(20),
    photo_url STRING(MAX),
    role_id STRING(MAX),
    updated_at TIMESTAMP,
    updated_by STRING(MAX),
) PRIMARY KEY (id)

CREATE TABLE organizations (
	id STRING(MAX) NOT NULL,
	address STRING(MAX),
	created_at TIMESTAMP,
	created_by STRING(MAX),
	is_deleted BOOL,
	logo STRING(MAX),
	name STRING(MAX),
	state STRING(MAX),
	sub_domain STRING(MAX),
	updated_at TIMESTAMP,
	updated_by STRING(MAX),
	zip_code STRING(20),
) PRIMARY KEY (id)

CREATE TABLE roles (
	id STRING(MAX) NOT NULL,
	created_at TIMESTAMP,
	created_by STRING(MAX),
	is_deleted BOOL,
	name STRING(50),
	updated_at TIMESTAMP,
	updated_by STRING(MAX),
) PRIMARY KEY (id)
