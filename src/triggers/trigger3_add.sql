-- description: add highest price to the auction when new bid arrives
drop trigger if exists auction_highest_price_on_new_bid;

create trigger auction_highest_price_on_new_bid
    after insert
    on bid
begin
    update auction
    set highest_bid=new.amount
    where id = new.auction_id;
end;