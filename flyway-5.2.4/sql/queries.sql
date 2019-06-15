-- 1. Find the number of users in the database.
-- Answer: 13422
-- my answer: 13419 (pending email with professor whether this is common error)
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


-- 4. Find the ID(s) of auction(s) with the highest current price.
-- Answer: 1046871451
-- my answer: 1046740686 (reference email with professor, my answer is the correct answer)
select item_id
from (select *, max(amount) from bid);


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


