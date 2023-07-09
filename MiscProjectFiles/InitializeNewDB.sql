create table Players(
    id integer primary key autoincrement,
    player_first_name text not null,
    player_last_name text not null,
    player_full_name as (player_first_name || ' ' || player_last_name),
    unique(player_first_name, player_last_name)
                    );

--insert into Players(player_first_name, player_last_name) values ('Andrew', 'McSparron');

create table BankAccounts(
    id integer primary key autoincrement,
    player_id integer not null,
    account_balance integer not null default 250,
    foreign key(player_id)
        references Players(id)
                         );

create table PlayersBankAccounts(
    player_id integer not null,
    account_id integer not null,
    foreign key(player_id)
        references Players (id),
    foreign key(account_id)
        references BankAccounts (id),
    primary key(player_id, account_id)
                                );

-- insert into BankAccounts(player_id) values (1);


create view PlayerBanksFull as
    select P.id as PlayerID,
           P.player_full_name as PlayerName,
           BA.id as AccountID,
           BA.account_balance
    from PlayersBankAccounts
        join BankAccounts BA on BA.id = PlayersBankAccounts.account_id
        join Players P on P.id = BA.player_id;
