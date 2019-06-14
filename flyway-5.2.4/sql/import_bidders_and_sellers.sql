drop table temp_user;

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

alter table user
    add column seller boolean;

update user
set seller =
        (
            select true
            from seller
            where seller.id = user.id
        )
where exists
          (
              select *
              from seller
              where seller.id = user.id
          );

alter table user
    add column bidder boolean;

update user
set bidder =
        (
            select true
            from bidder
            where bidder.id = user.id
        )
where exists
          (
              select *
              from bidder
              where bidder.id = user.id
          );


