CREATE TABLE IF NOT EXISTS sessions (
  session_id char(128) UNIQUE NOT NULL,
  atime timestamp NOT NULL default current_timestamp,
  data text
);

CREATE TABLE IF NOT EXISTS conversations (
  conversation_id char(36) UNIQUE NOT NULL,
  atime integer NOT NULL,
  data text
);