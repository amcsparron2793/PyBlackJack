create table Players(
    id integer primary key autoincrement,
    player_first_name text not null,
    player_last_name text not null,
    player_full_name as (player_first_name || ' ' || player_last_name),
    unique(player_first_name, player_last_name)
                    );

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

create view PlayerBanksFull as
    select P.id as PlayerID,
           P.player_full_name as PlayerName,
           BA.id as AccountID,
           BA.account_balance
    from PlayersBankAccounts
        join BankAccounts BA on BA.id = PlayersBankAccounts.account_id
        join Players P on P.id = BA.player_id;

create table WinLossRecords(
    id integer primary key autoincrement not null,
    player_id int not null unique,
    Wins int not null default 0,
    Losses int not null default 0,
    foreign key(player_id)
        references Players(id));

create table LastGamePlayed(
    id integer primary key autoincrement not null,
    player_id integer not null,
    date_of_game datetime not null,
     foreign key(player_id)
        references Players(id));
