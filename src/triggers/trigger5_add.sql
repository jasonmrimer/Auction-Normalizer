-- description: denies bids that are not within the auction window
drop trigger if exists bid_time_must_be_within_auction_time;

create trigger bid_time_must_be_within_auction_time
    before insert
    on bid
begin
    select case
               when
                   (
                           new.time <
                           (
                               select start
                               from auction
                               where auction.id = new.auction_id
                           )
                       )
                   then
                   raise(abort, 'Bids must be after the auction starts.')
               when
                   (
                           new.time >
                           (
                               select end
                               from auction
                               where auction.id = new.auction_id
                           )
                       )
                   then
                   raise(abort, 'Bids must be before the auction ends.')
               end;
end;