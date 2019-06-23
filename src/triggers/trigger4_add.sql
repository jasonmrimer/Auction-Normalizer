-- description: deny the seller of an auction the ability to bid on that auction
drop trigger if exists seller_cannot_bid_on_auction;

create trigger seller_cannot_bid_on_auction
    before insert
    on bid
    when
        (
                new.user_id = (
                select seller_id
                from auction
                where auction.id = new.auction_id
            )
            )
begin
    select raise ( abort, 'Sellers may not bid on their own auction.' );
end;