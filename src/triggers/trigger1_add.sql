-- description: add new users when bidding without existing user
drop trigger if exists bid_with_new_user;

create trigger bid_with_new_user
    before insert
    on bid
    when
        (
            select id
            from user
            where new.user_id = user.id
        ) isnull
begin
    insert into user (id, rating, location_id)
    VALUES (new.user_id, 0, null);
end;

