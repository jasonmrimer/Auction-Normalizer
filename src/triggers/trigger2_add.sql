-- description: add new users when auctioning without existing user
drop trigger if exists auction_with_new_seller;

create trigger auction_with_new_seller
    before insert
    on auction
    when
        (
            select id
            from user
            where new.seller_id = user.id
        ) isnull
begin
    insert into user (id, rating, location_id)
    VALUES (new.seller_id, 0, null);
end;

