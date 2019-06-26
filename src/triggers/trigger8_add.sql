-- description: new bids occur at pseudo current time
drop trigger if exists all_new_bids_occur_at_pseudo_now;

create trigger all_new_bids_occur_at_pseudo_now
    after insert
    on bid
begin
    update bid
    set time =
            (
                select now
                from pseudo_time
            )
    where bid.auction_id = new.auction_id
      and bid.user_id = new.user_id
      and bid.amount = new.amount;
end;