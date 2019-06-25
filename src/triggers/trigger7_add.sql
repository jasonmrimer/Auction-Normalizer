-- description: bid prices must exceed current best
drop trigger if exists new_bids_exceed_current_highest_bid;

create trigger new_bids_exceed_current_highest_bid
    before insert
    on bid
    when
            new.amount <
            (
                select max(amount) high
                from bid
                where new.auction_id = bid.auction_id
            )
begin
    select raise(
                   abort,
                   'New bids must exceed the current highest bid.'
               );
end;