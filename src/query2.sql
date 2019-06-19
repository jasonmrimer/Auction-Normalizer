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