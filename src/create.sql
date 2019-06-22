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
    name varchar(64)
);

create table country
(
    id   integer PRIMARY KEY autoincrement,
    name varchar(64)
);

create table location
(
    id           integer primary key autoincrement,
    name         text,
    country_name text
);

create table user
(
    id   varchar(64) PRIMARY KEY,
    rating integer,
    location_name varchar(128),
    country_name varchar(64)
);

create table bid
(
    auction_id integer,
    user_id varchar(64),
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
