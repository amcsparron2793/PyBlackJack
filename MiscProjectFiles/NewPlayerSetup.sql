-- New player setup
insert into Players(player_first_name, player_last_name)
values (
        :fname,
        :lname
        );

insert into BankAccounts(player_id)
values (
        (select max(id) from Players)
        );

insert into PlayersBankAccounts(player_id, account_id)
values(
       (select max(id) from Players),
       (select max(id) from BankAccounts)
       );