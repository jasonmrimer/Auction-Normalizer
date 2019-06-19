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