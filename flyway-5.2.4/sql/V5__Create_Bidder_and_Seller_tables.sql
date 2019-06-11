create table seller
(
    id            varchar(64) PRIMARY KEY,
    rating        integer,
    location_name varchar(128),
    country_name  varchar(64)
);

create table bidder
(
    id            varchar(64) PRIMARY KEY,
    rating        integer,
    location_name varchar(128),
    country_name  varchar(64)
);
