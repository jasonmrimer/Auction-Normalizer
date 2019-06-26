-- description: pseudo time only moves forward, denies moving time back
drop trigger if exists pseudo_time_moves_forward;

create trigger pseudo_time_moves_forward
    before insert
    on pseudo_time
    when new.now <
         (select now from pseudo_time)
begin
    select raise(abort, 'Users may only move the pseudo time forward.');
end;