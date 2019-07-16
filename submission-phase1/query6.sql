-- 6. Find the number of users who are both sellers and bidders.
-- Answer: 6717
-- my answer: 6717
select count(*)
from (
         select distinct auction.seller_id
         from auction
                  inner join bid on bid.user_id = auction.seller_id
     );