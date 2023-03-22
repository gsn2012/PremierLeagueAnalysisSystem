DROP TABLE IF EXISTS Managers CASCADE;
DROP TABLE IF EXISTS Referees CASCADE;
DROP TABLE IF EXISTS Positions CASCADE;
DROP TABLE IF EXISTS Stadiums CASCADE;
DROP TABLE IF EXISTS Teams_Owner_Managed_Located CASCADE;
DROP TABLE IF EXISTS Standings_Pertain_to CASCADE;
DROP TABLE IF EXISTS Players_Plays_In_Plays_for CASCADE;
DROP TABLE IF EXISTS Matches_Held_at CASCADE;
DROP TABLE IF EXISTS Officiated_by CASCADE;
DROP TABLE IF EXISTS Teams_Play_Matches CASCADE;
DROP TABLE IF EXISTS Goals_Scored CASCADE;


create table Managers (
    id integer primary key,
    name varchar(128),
    age integer,
    nationality varchar(128)
);

create table Referees (
	id integer primary key,
	name varchar(128),
	nationality varchar(128)
);

create table Positions (
	pos varchar(128) primary key,
	pos_type varchar(128)
);

create table Stadiums (
	id integer primary key,
	name varchar(128),
	address varchar(128)
);

create table Teams_Owner_Managed_Located (
	id integer primary key,
	name varchar(128),
	establishment_year integer,
	city varchar(128),
	titles integer,
	owner_id integer unique not null,
	owner_name varchar(128),
	owner_age integer,
	owner_net_worth decimal,
	manager_id integer unique not null,
	stadium_id integer unique not null,
	foreign key (manager_id) references Managers(id),
	foreign key (stadium_id) references Stadiums(id)
);

create table Standings_Pertain_to (
	id integer,
	pld integer,
	wins integer,
	draws integer,
	losses integer,
	gf integer,
	ga integer,
	points integer,
	T_id integer,
	primary key (T_id, id),
	foreign key (T_id) references Teams_Owner_Managed_Located(id) on delete cascade
);

create table Players_Plays_In_Plays_for (
	id integer primary key,
	name varchar(128),
	age integer,
	nationality varchar(128),
	jersey_number integer,
	foot char(10),
	pos varchar(128) not null,
	captain boolean,
	T_id integer not null,
	appearances integer,
	substitutions integer,	
	goals integer,
	penalties integer,
	yellow_cards integer,	
	red_cards integer,
	foreign key (pos) references Positions(pos),
	foreign key (T_id) references Teams_Owner_Managed_Located(id)
);

create table Matches_Held_at (
	id integer primary key,
	team1_id integer,
	team2_id integer,
	h_score integer,
	a_score integer,
	match_date date,
	captain1_id integer not null,
	captain2_id integer not null,
	stadium_id integer not null,
	foreign key (stadium_id) references Stadiums(id),
	foreign key (captain1_id) references Players_Plays_In_Plays_for(id),
	foreign key (captain2_id) references Players_Plays_In_Plays_for(id)
);

create table Officiated_by (
	match_id integer,
	referee_id integer,
	primary key (match_id, referee_id),
	foreign key (match_id) references Matches_held_at(id),
	foreign key (referee_id) references Referees(id)
);

create table Teams_Play_Matches (
	match_id integer,
	team1_id integer,
	team2_id integer,
	primary key (match_id, team1_id, team2_id),
	foreign key (match_id) references Matches_Held_at(id),
	foreign key (team1_id) references Teams_Owner_Managed_Located(id),
	foreign key (team2_id) references Teams_Owner_Managed_Located(id)
);

create table Goals_Scored (
	id integer primary key,
	pen boolean,
	goal_time integer,
	winner boolean,
	equalizer boolean,
	own_goal boolean,
	player_id integer not null,
	match_id integer not null,
	foreign key (player_id) references Players_Plays_In_Plays_for(id),
	foreign key (match_id) references Matches_Held_at(id)
);
