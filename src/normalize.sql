CREATE TABLE location2
(
    id         integer primary key,
    name       varchar(128),
    country_id integer,
    FOREIGN KEY (country_id) references country (id)
);

insert into location2
select location.id, location.name, country.id
from location
         left join country on country.name = location.country_name;

drop table location;

alter table location2 rename to location;

