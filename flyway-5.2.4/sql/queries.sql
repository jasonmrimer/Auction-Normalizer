-- 1. Find the number of users in the database.
-- Answer: 13422
-- my answer: 13422
select count(*)
from user;


-- 2. Find the number of users from New York (i.e., users whose location is the string ”New York”).
-- Answer: 80
-- my answer: 80
select count(*)
from user,
     (
         select location.id as lid
         from location
         where location.name = 'New York'
     )
where user.location_id = lid;


-- 3. Find the number of auctions belonging to exactly four categories.
-- Answer: 8365
-- my answer: 8365
select count(*)
from (
         select auction_id, count(*)
         from join_auction_category
         group by auction_id
         having count(*) = 4
     );


-- 4. Find the ID(s) of auction(s) with the highest current price.
-- Answer: 1046871451
-- my answer: 1046740686*
-- * reference email with professor, my answer is the correct answer
select auction_id
from (select *, max(amount) from bid);


-- 5. Find the number of sellers whose rating is higher than 1000.
-- Answer: 3130
-- my answer: 3130
select count(*)
from (
         select distinct seller_id
         from auction
                  inner join user on user.id = seller_id
         where user.rating > 1000
     );


-- 6. Find the number of users who are both sellers and bidders.
-- Answer: 6717
-- my answer: 6717
select count(*)
from (
         select distinct auction.seller_id
         from auction
                  inner join bid on bid.user_id = auction.seller_id
     );


-- 7. Find the number of categories that include at least one item with a bid of more than $100.
-- Answer: 150
-- my answer: 150
select count(*)
from (
         select distinct category_id
         from join_auction_category jac
                  inner join
              (
                  select bid.auction_id
                  from bid
                  where amount > 100
              ) b
              on jac.auction_id = b.auction_id
     );
