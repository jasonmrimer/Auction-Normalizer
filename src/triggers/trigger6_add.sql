-- description: auctions must update number of bids when bids are added
drop trigger if exists new_bids_update_auction_number_of_bids;

create trigger new_bids_update_auction_number_of_bids
    after insert
    on bid
begin
    update auction
    set number_of_bids=
            (
                select count(*)
                from bid
                where auction_id = new.auction_id
            )
    where id = new.auction_id;
end;