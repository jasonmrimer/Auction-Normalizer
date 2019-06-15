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

alter table temp_join_a_c rename to join_auction_category;
