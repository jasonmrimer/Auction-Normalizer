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