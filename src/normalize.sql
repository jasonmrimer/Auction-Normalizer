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



create table temp_join_a_c
(
    id          integer primary key,
    auction_id  integer,
    category_id integer
);

insert into temp_join_a_c
select join_auction_category.id, auction.id, category.id
from join_auction_category
         left join auction on auction.id = join_auction_category.auction_id
         left join category on category.name = join_auction_category.category;

drop table join_auction_category;

alter table temp_join_a_c
    rename to join_auction_category;

create table temp_bid
(
    auction_id integer,
    user_id    integer,
    time       datetime,
    amount     float,
    foreign key (auction_id) references auction (id),
    foreign key (user_id) references user (id),
    primary key (auction_id, user_id, time, amount)
);

insert into temp_bid
select auction.id, user.id, bid.time, bid.amount
from bid
         left join auction on auction.id = bid.item_id
         left join user on user.id = bid.user_id;

drop table bid;

alter table temp_bid
    rename to bid;

alter table auction
    add column number_of_bids integer;

alter table auction
    add column highest_bid float;

update auction
set number_of_bids =
        (
            select count(*)
            from bid
            where bid.auction_id = auction.id
        );

update auction
set highest_bid =
        (
            select max(amount)
            from bid
            where bid.auction_id = auction.id
        );

update auction
set buy_price = null
where buy_price = 'NULL';