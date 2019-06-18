create table temp_join_a_c
(
    id          integer primary key,
    auction_id  integer,
    category_id integer,
    foreign key (auction_id) references auction (id),
    foreign key (category_id) references category (id)
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



create table temp_auction
(
    id             integer primary key,
    name           text,
    starting_price float,
    start          datetime,
    end            datetime,
    description    text,
    buy_price      text,
    seller_id      text,
    number_of_bids integer,
    highest_bid float,
    foreign key (seller_id) references user (id)
);

insert into temp_auction
select auction.id,
       auction.name,
       auction.starting_price,
       auction.start,
       auction.end,
       auction.description,
       auction.buy_price,
       user.id,
       null,
       null
from auction
         left join user on auction.seller_id = user.id;

drop table auction;

alter table temp_auction
rename to auction;

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
