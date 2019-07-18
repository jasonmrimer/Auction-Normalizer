-- description: denies bids that are not within the auction window
drop trigger if exists bid_time_must_be_within_auction_time;