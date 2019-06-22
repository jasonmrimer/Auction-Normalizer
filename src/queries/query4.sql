-- 4. Find the ID(s) of auction(s) with the highest current price.
-- Answer: 1046871451
-- my answer: 1046740686*
-- * reference email with professor, my answer is the correct answer
select auction_id
from (select *, max(amount) from bid);