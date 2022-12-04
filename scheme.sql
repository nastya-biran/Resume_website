drop table if exists user;
create table user (
    username text not null,
    password text not null,
    name text,
    surname text,
    age integer,
    education text,
    job_position text,
    previous_workplace text,
    projects text
);
INSERT INTO user
VALUES ("admin", "default","Anastasiya","Biran","","","","","");

