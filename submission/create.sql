drop table if exists category;
drop table if exists country;
drop table if exists location;
drop table if exists user;
drop table if exists bid;
drop table if exists auction;
drop table if exists join_auction_category;

create table category
(
    id   integer PRIMARY KEY autoincrement,
    name text unique on conflict abort
);

create table country
(
    id   integer PRIMARY KEY autoincrement,
    name text unique
);

create table location
(
    id           integer primary key autoincrement,
    name         text,
    country_name text,
    UNIQUE (name, country_name)
);

create table user
(
    id   text PRIMARY KEY,
    rating integer,
    location_name text,
    country_name text
);

create table bid
(
    auction_id integer,
    user_id text,
    time    datetime,
    amount  float
);

create table auction(
    id integer primary key,
    name text,
    starting_price float,
    start datetime,
    end datetime,
    description text,
    buy_price float,
    seller_id text
);

create table join_auction_category
(
    id integer primary key,
    auction_id integer,
    category text
);
