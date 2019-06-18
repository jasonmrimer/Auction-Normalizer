create table location2
(
    id         integer primary key,
    name       varchar(128),
    country_id integer,
    foreign key (country_id) references country (id)
);

insert into location2
select location.id, location.name, country.id
from location
         left join country on country.name = location.country_name;

drop table location;

alter table location2 rename to location;



create table temp_user
(
    id            varchar(64) primary key,
    rating        integer,
    location_name varchar(128),
    country_id    integer,
    foreign key (country_id) references country (id)
);

create table temp_user2
(
    id          varchar(64) primary key,
    rating      integer,
    location_id integer,
    foreign key (location_id) references location (id)
);

insert into temp_user
select user.id, user.rating, user.location_name, country.id
from user
         left join country on country.name = user.country_name;

insert into temp_user2
select temp_user.id, temp_user.rating, location.id
from temp_user
         left join location on location.name = temp_user.location_name
    and location.country_id = temp_user.country_id;

drop table user;
drop table temp_user;

alter table temp_user2
    rename to user;
