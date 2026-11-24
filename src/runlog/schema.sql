create table if not exists users(
    id integer primary key,
    email text unique not null,
    password_hash text not null
);

create table if not exists tags(
    id integer primary key,
    name text unique not null
);

create table if not exists runs (
    id integer unique primary key,
    user_id integer not null references user(id),
    run_date date not null,
    distance_km float not null,
    duration_seconds integer not null,
    run_type text,
    notes text
);

create table if not exists run_tags (
    run_id integer not null references runs(id),
    tag_id integer not null references tags(id),
    primary key (run_id, tag_id)
);
