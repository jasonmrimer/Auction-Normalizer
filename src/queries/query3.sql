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