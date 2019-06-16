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
