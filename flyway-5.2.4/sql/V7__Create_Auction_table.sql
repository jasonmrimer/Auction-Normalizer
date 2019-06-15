create table auction(
    id integer primary key,
    name text,
    starting_price float,
    start datetime,
    end datetime,
    description text,
    buy_price text,
    seller_id text
)