CREATE TABLE "team" (
  "id" INT PRIMARY KEY NOT NULL,
  "full_name" VARCHAR(30) NOT NULL,
  "abbreviation" VARCHAR(30) NOT NULL,
  "nickname" VARCHAR(30) NOT NULL,
  "city" VARCHAR(30) NOT NULL,
  "state" VARCHAR(30) NOT NULL,
  "year_founded" INT,
  "creation_timestamp" TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

COMMENT on TABLE team IS 'The NBA team'