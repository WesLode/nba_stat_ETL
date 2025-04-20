CREATE TABLE "player" (
  "id" INT PRIMARY KEY NOT NULL,
  "full_name" VARCHAR(30) NOT NULL,
  "first_name" VARCHAR(30) NOT NULL,
  "last_name" VARCHAR(30) NOT NULL,
  "is_active" BOOLEAN NOT NULL,
  "creation_timestamp" TIMESTAMPTZ DEFAULT NOW() NOT NULL

);

COMMENT on TABLE player IS 'The NBA player name from the collective history'
