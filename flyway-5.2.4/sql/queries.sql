-- 1. Find the number of users in the database.
-- Answer: 13422
-- my answer: 13419
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


-- 5. Find the number of sellers whose rating is higher than 1000.
-- Answer: 3130
-- my answer: 3130
select count(*)
from user
where seller = true and rating > 1000;

-- 6. Find the number of users who are both sellers and bidders.
-- Answer: 6717
-- my answer: 3442
select count(*)
from user
where seller = true and bidder = true;
