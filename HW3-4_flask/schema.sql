drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  country text not null,
  title text not null,
  link text not null,
  author text,
  content text
);