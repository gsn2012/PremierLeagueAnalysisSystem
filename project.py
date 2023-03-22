import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser

@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)
    
    # Obtain data
    data = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

st.title('Premier League 2021-22 Season Analysis')

menu = ["Home","Teams", "Players", "Managers", "Stadiums", "Referees"]
choice = st.sidebar.selectbox("Menu",menu)

if choice == "Home":
    st.subheader("Home")

    with st.expander("Tables"):
        sql = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
        try:
            all_table_names = query_db(sql)["relname"].tolist()
            table_name = st.selectbox("Choose a table", all_table_names)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")

        if table_name:
            f"Display the table"

            sql_table = f"SELECT * FROM {table_name};"
            try:
                df = query_db(sql_table)
                st.dataframe(df)
            except:
                st.write("Sorry! Something went wrong with your query, please try again.")

    st.markdown("## Principles of Database Systems Project")
    st.markdown("##### - By -")
    st.markdown("### Sourabh Kumar Bhattacharjee (skb5275)")
    st.markdown("### Gautam Suresh Nambiar (gsn2012)")


elif choice  == "Teams":
    st.subheader("Teams")
    menuTeams = [
                'Goals Scored By Teams',
                'Goals Conceded By Teams',
                'Teams With Fewest Losses',
                'Top GoalScoring Teams From A Given City',
                'Avg Goals Scored - Derby Matches vs Non Derby Matches',
                'Top Teams By Number Of Penalties Awarded',
                'Teams With Most Clean Sheets'
            ]
    choiceTeams = st.selectbox("Menu", menuTeams)
    choiceTeams_num = menuTeams.index(choiceTeams)

    if choiceTeams_num == 0:                           
        with st.expander("Goals Scored By Teams",expanded=True):
            goals_scored_teams="""SELECT T.name team, S.gf goals_scored
                                    FROM Standings_Pertain_to S
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON S.T_id = T.id
                                    ORDER BY S.gf DESC;"""
            result = query_db(goals_scored_teams)
            st.dataframe(result)
            result = result.set_index('team')
            st.bar_chart(result)

    if choiceTeams_num == 1:                           
        with st.expander("Goals Conceded By Teams",expanded=True):
            goals_conceded_teams="""SELECT T.name team, S.ga goals_conceded
                                    FROM Standings_Pertain_to S
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON S.T_id = T.id
                                    ORDER BY S.ga DESC;"""
            result = query_db(goals_conceded_teams)
            st.dataframe(result)
            result = result.set_index('team')
            st.bar_chart(result)

    if choiceTeams_num == 2:                           
        with st.expander("Teams With Fewest Losses",expanded=True):
            fewest_losses_teams="""SELECT T.name team, S.losses
                                    FROM Standings_Pertain_to S
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON S.T_id = T.id
                                    ORDER BY S.losses;"""
            result = query_db(fewest_losses_teams)
            st.dataframe(result)
            result = result.set_index('team')
            st.bar_chart(result)

    if choiceTeams_num == 3:
        city = ['London', 'Manchester', 'Merseyside', 'Birmingham', 'Brighton and Hove', 'Lancashire', 
                'Leicester', 'Newcastle', 'Norwich', 'Southampton', 'Watford', 'Wolverhampton'
               ] 
        choiceCity = st.selectbox("Select A City", city)                 
        with st.expander("Top GoalScoring Teams",expanded=True):
            goals_scoring_teams_city=f"""SELECT T.name team, S.gf goals_scored
                                        FROM Standings_Pertain_to S
                                        INNER JOIN Teams_Owner_Managed_Located T
                                        ON S.T_id = T.id
                                        WHERE T.city = '{choiceCity}'
                                        ORDER BY S.gf DESC;"""
            st.table(query_db(goals_scoring_teams_city))
            result = query_db(goals_scoring_teams_city)
            result = result.set_index('team')
            st.bar_chart(result)

    if choiceTeams_num == 4:                           
        with st.expander("Avg Goals Scored - Derby Matches vs Non Derby Matches",expanded=True):
            avg_goals_scored_derby="""SELECT D.total_Derby_Goals, D.Derby_Goals_per_match, ND.total_Non_Derby_Goals, 
                                        ND.Non_Derby_Goals_per_match
                                        FROM
                                        (
	                                        SELECT ROUND(AVG(M.h_score + M.a_score), 2) Derby_Goals_per_match,
	                                        SUM(M.h_score + M.a_score) total_Derby_Goals
	                                        FROM Matches_Held_at M 
	                                        INNER JOIN Teams_Owner_Managed_Located H
	                                        ON M.team1_id = H.id
	                                        INNER JOIN Teams_Owner_Managed_Located A
	                                        ON M.team2_id = A.id
	                                        WHERE H.city = A.city
                                        ) D,
                                        (
	                                        SELECT ROUND(AVG(M.h_score + M.a_score), 2) Non_Derby_Goals_per_match,
                                            SUM(M.h_score + M.a_score) total_Non_Derby_Goals
                                            FROM Matches_Held_at M
                                            INNER JOIN Teams_Owner_Managed_Located H
                                            ON M.team1_id = H.id
                                            INNER JOIN Teams_Owner_Managed_Located A
                                            ON M.team2_id = A.id
                                            WHERE H.city != A.city
                                        ) ND;"""
            result = query_db(avg_goals_scored_derby)
            st.dataframe(result.style.format({"D.Derby_Goals_per_match": "{:.2f}", "ND.Non_Derby_Goals_per_match": "{:.2f}"}))

    if choiceTeams_num == 5:                           
        with st.expander("Top Teams By Number Of Penalties Awarded",expanded=True):
            goals_scored_teams="""SELECT T.name team, 
                                    SUM(CASE WHEN G.pen THEN 1 ELSE 0 END) num_Penalties, 
                                    CAST(COUNT(G.id) as decimal) totalGoals,
                                    100*ROUND(SUM(CASE WHEN G.pen THEN 1.0 ELSE 0.0 END)/CAST(COUNT(G.id) as decimal), 4) percentage_Penalties
                                    FROM Goals_Scored G
                                    INNER JOIN Players_Plays_In_Plays_for P
                                    ON G.player_id = P.id
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON P.T_id = T.id
                                    GROUP BY T.id, T.name
                                    ORDER BY percentage_Penalties DESC;"""
            result = query_db(goals_scored_teams)
            st.table(result.style.format({"percentage_Penalties": "{:.2f}"}))

    if choiceTeams_num == 6:                           
        with st.expander("Teams With Most Clean Sheets",expanded=True):
            clean_sheet_teams="""SELECT X.Team Team, SUM(X.CleanSheets) CleanSheets, SUM(X.TotalMatches) TotalMatches, 100*ROUND((SUM(X.CleanSheets)/SUM(X.TotalMatches)),4) CleanSheetPercentage
                                    FROM (
                                    SELECT T.Name Team, SUM(CASE WHEN M.a_score = 0 THEN 1 ELSE 0 END) CleanSheets, COUNT(M.id) TotalMatches
                                    FROM Matches_Held_At M
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON T.id = M.team1_id
                                    GROUP BY Team
                                    UNION ALL
                                    SELECT T.Name Team, SUM(CASE WHEN M.h_score = 0 THEN 1 ELSE 0 END) CleanSheets, COUNT(M.id) TotalMatches
                                    FROM Matches_Held_At M
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON T.id = M.team2_id
                                    GROUP BY Team) X
                                    GROUP BY Team
                                    ORDER BY CleanSheets DESC;"""
            result = query_db(clean_sheet_teams)
            st.table(result.style.format({"CleanSheetPercentage": "{:.2f}"}))


elif choice == "Players":
    st.subheader("Players")

    menuPlayers = [
                'Top Goal Scorers',
                'Players With Most Hattricks',
                'Goal Scorers By Position And Nationality',
                'Players With Maximum Winners',
                'Players With Maximum Equalizers',
                'Goalscorers Above Certain Age',
                'Goalscorers Below Certain Age',
                'Captains With The Most Goals'
            ]
    choicePlayers = st.selectbox("Menu", menuPlayers)
    choicePlayers_num = menuPlayers.index(choicePlayers)

    if choicePlayers_num == 0:                           
        sql = "SELECT name FROM Teams_Owner_Managed_Located;"
        try:
            all_team_names = query_db(sql)["name"].tolist()
            team_name = st.multiselect("Select Team(s):", all_team_names)
            if len(team_name) == 0:
                team_name = tuple(all_team_names)
            elif len(team_name) == 1:
                team_name = (team_name[0], team_name[0])
            else:
                team_name = tuple(team_name)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")
        
        with st.expander("Top Goalscorers",expanded=True):
            goals_players=f"""SELECT P.name Player, T.name Team, COUNT(G.id) Goals
                                FROM Goals_Scored G
                                INNER JOIN Players_Plays_in_Plays_for P
                                ON G.player_id = P.id
                                INNER JOIN Teams_Owner_Managed_Located T
                                ON P.t_id = T.id
                                WHERE T.name in {team_name}
                                GROUP BY G.player_id, P.name, T.name
                                ORDER BY Goals DESC;"""
            st.dataframe(query_db(goals_players))

    if choicePlayers_num == 1:                           
        with st.expander("Players With Most Hattricks",expanded=True):
            hattrick_players="""SELECT P.name Player, T.name Team, SUM(H.Hattricks) Hattricks
                                FROM Players_Plays_in_Plays_for P
                                INNER JOIN Teams_Owner_Managed_Located T
                                ON P.t_id = T.id
                                INNER JOIN  (
                                SELECT G.player_id id, G.match_id match_id, (COUNT(G.id)/3) Hattricks
                                FROM Goals_Scored G
                                GROUP BY G.player_id, G.match_id
                                having COUNT(G.id) >= 3
                                ) H
                                ON H.id = P.id
                                GROUP BY Player, Team
                                ORDER BY Hattricks DESC;"""
            st.table(query_db(hattrick_players))

    if choicePlayers_num == 2:
        position = st.radio("Choose a position", ("Forward", "Midfielder", "Defender"))                           
        
        sql = f"SELECT pos FROM Positions WHERE pos_type = '{position}';"
        try:
            pos_names = query_db(sql)["pos"].tolist()
            pos_name = st.multiselect("Select Field Position(s):", pos_names)
            if len(pos_name) == 0:
                pos_name = tuple(pos_names)
            elif len(pos_name) == 1:
                pos_name = (pos_name[0], pos_name[0])
            else:
                pos_name = tuple(pos_name)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")
        
        with st.expander("Goal Scorers By Position And Nationality",expanded=True):
            goals_players_position=f"""SELECT P.nationality country, COUNT(distinct G.player_id) goalScoringPlayers, 
                                        COUNT(G.id) totalGoalsScoredByPosition
                                        FROM Players_Plays_in_Plays_for P
                                        INNER JOIN Positions Pos
                                        ON P.pos = Pos.pos
                                        INNER JOIN Goals_Scored G
                                        ON G.player_id = P.id
                                        WHERE Pos.pos_type = '{position}'
                                        AND Pos.pos in {pos_name}
                                        GROUP BY country
                                        ORDER BY totalGoalsScoredByPosition DESC;"""
            st.table(query_db(goals_players_position))

    if choicePlayers_num == 3:                           
        with st.expander("Players With Maximum Winners",expanded=True):
            winners_players="""SELECT P.name player, T.name team, SUM(CASE WHEN winner THEN 1 ELSE 0 END) cntWinners,
                                CAST(COUNT(G.id) AS decimal) totalGoals,
                                100*ROUND(SUM(CASE WHEN winner THEN 1.0 ELSE 0.0 END)/CAST(COUNT(G.id) AS decimal), 4) winnerPercentage
                                FROM Goals_Scored G
                                INNER JOIN Players_Plays_In_Plays_for P
                                ON G.player_id = P.id
                                INNER JOIN Teams_Owner_Managed_Located T
                                ON P.T_id = T.id
                                GROUP BY G.player_id, P.name, T.name
                                HAVING COUNT(G.id) > 1
                                ORDER BY cntWinners DESC
                                LIMIT 20;"""
            result = query_db(winners_players)
            st.dataframe(result.style.format({"winnerPercentage": "{:.2f}"}))

    if choicePlayers_num == 4:                     
        with st.expander("Players With Maximum Equalizers",expanded=True):
            equilizers_players="""SELECT P.name player, T.name team, SUM(CASE WHEN equalizer THEN 1 ELSE 0 END) cntEqualizers,
                                    CAST(COUNT(G.id) AS decimal) totalGoals,
                                    100*ROUND(SUM(CASE WHEN equalizer THEN 1.0 ELSE 0.0 END)/CAST(COUNT(G.id) AS decimal), 4) equalizerPercentage
                                    FROM Goals_Scored G
                                    INNER JOIN Players_Plays_In_Plays_for P
                                    ON G.player_id = P.id
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON P.T_id = T.id
                                    GROUP BY G.player_id, P.name, T.name
                                    HAVING COUNT(G.id) > 1
                                    ORDER BY cntEqualizers DESC
                                    LIMIT 20;"""
            result = query_db(equilizers_players)
            st.dataframe(result.style.format({"equalizerPercentage": "{:.2f}"}))

    if choicePlayers_num == 5: 
        age = st.slider('Enter Minumum Age: ', 15, 45, 30)                          
        with st.expander("Goalscorers Above Certain Age",expanded=True):
            old_goals_score_players=f"""SELECT P.name player, T.name team, P.age, CAST(COUNT(G.id) AS decimal) totalGoals
                                        FROM Goals_Scored G
                                        INNER JOIN Players_Plays_In_Plays_for P
                                        ON G.player_id = P.id
                                        INNER JOIN Teams_Owner_Managed_Located T
                                        ON P.T_id = T.id
                                        WHERE P.age >= {age}
                                        GROUP BY G.player_id, P.name, P.age, T.name
                                        ORDER BY totalGoals DESC,  P.age DESC;"""
            st.dataframe(query_db(old_goals_score_players))

    if choicePlayers_num == 6:                           
        age = st.number_input('Enter Maximum Age: ', value = 20)
        with st.expander("Goalscorers Below Certain Age",expanded=True):    
            young_goals_score_players=f"""SELECT P.name player, T.name team, P.age, CAST(COUNT(G.id) AS decimal) totalGoals
                                            FROM Goals_Scored G
                                            INNER JOIN Players_Plays_In_Plays_for P
                                            ON G.player_id = P.id
                                            INNER JOIN Teams_Owner_Managed_Located T
                                            ON P.T_id = T.id
                                            WHERE P.age <= {age}
                                            GROUP BY G.player_id, P.name, P.age, T.name
                                            ORDER BY totalGoals DESC,  P.age DESC;"""
            st.dataframe(query_db(young_goals_score_players))
    
    if choicePlayers_num == 7:                           
        with st.expander("Captains With The Most Goals",expanded=True):
            captain_goals_score_players="""SELECT P.name Player, T.name Team, COUNT(G.id) Goals
                                            FROM Players_Plays_in_Plays_for P
                                            INNER JOIN Goals_Scored G
                                            ON G.player_id = P.id
                                            INNER JOIN Teams_Owner_Managed_Located T
                                            ON P.t_id = T.id
                                            WHERE P.captain is TRUE
                                            GROUP BY G.player_id, P.name, T.name
                                            ORDER BY Goals DESC;"""
            st.dataframe(query_db(captain_goals_score_players))

elif choice == "Managers":
    st.subheader("Managers")
    menuManagers = [
                'Manager Wins By Nationality',
                'Managers With Highest Percentage Of Players Of Their Own Nationalities',
                'Managers with most home wins / away wins'
            ]
    choiceManagers = st.selectbox("Menu", menuManagers)
    choiceManagers_num = menuManagers.index(choiceManagers)

    if choiceManagers_num == 0:                           
        with st.expander("Manager Wins By Nationality",expanded=True):
            wins_managers="""SELECT X.nationality Manager_Nationality, 
                                STRING_AGG (
                                                X.name||' ('||X.team||')',
                                                ', '
                                                ORDER BY
                                                X.name
                                        ) managers,
                                SUM(wins) total_wins, 
                                AVG(win_percentage) average_win_percentage
                                FROM
                                (
                                    SELECT M.id, M.name, M.nationality, T.id T_id, T.name team, S.wins, 
                                    100*ROUND(CAST(S.wins AS decimal)/CAST(S.wins + S.losses + S.draws AS decimal),4) win_percentage 
                                    FROM Managers M
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON M.id = T.manager_id
                                    INNER JOIN Standings_Pertain_to S
                                    ON T.id = S.T_id
                                ) X
                                GROUP BY X.nationality
                                ORDER BY AVG(win_percentage) DESC;"""
            result = query_db(wins_managers)
            st.dataframe(result.style.format({"average_win_percentage": "{:.2f}"}))

    if choiceManagers_num == 1:                           
        with st.expander("Managers With Highest Percentage Of Players Of Their Own Nationalities",expanded=True):
            managers_nationality="""SELECT Y.id, Y.manager_name, Y.team, Y.nationality,
                                    COALESCE(X.cnt_compatriot_players, 0) cnt_compatriot_players, 
                                    100*ROUND(CAST(COALESCE(X.cnt_compatriot_players,0) AS decimal)/CAST(Y.cnt_players AS decimal),4) compatriot_player_percentage
                                    FROM
                                    (
                                        SELECT M.id, M.name manager_name, T.name team, M.nationality, COUNT(P.id) cnt_compatriot_players
                                        FROM Managers M
                                        LEFT OUTER JOIN Teams_Owner_Managed_Located T
                                        ON M.id = T.manager_id
                                        LEFT OUTER JOIN Players_Plays_In_Plays_for P
                                        ON T.id = P.T_id
                                        WHERE M.nationality = p.Nationality
                                        GROUP BY M.id, M.name, T.name, M.nationality
                                    ) X
                                    RIGHT OUTER JOIN
                                    (
                                        SELECT M.id, M.name manager_name, T.name team, M.nationality, COUNT(P.id) cnt_players
                                        FROM Managers M
                                        LEFT OUTER JOIN Teams_Owner_Managed_Located T
                                        ON M.id = T.manager_id
                                        LEFT OUTER JOIN Players_Plays_In_Plays_for P
                                        ON T.id = P.T_id
                                        GROUP BY M.id, M.name, T.name, M.nationality
                                    ) Y
                                    ON X.id = Y.id
                                    AND X.manager_name = Y.manager_name
                                    AND X.team = Y.team
                                    AND X.nationality = Y.nationality
                                    ORDER BY compatriot_player_percentage DESC;"""
            result = query_db(managers_nationality)
            st.dataframe(result.style.format({"compatriot_player_percentage": "{:.2f}"}))

    if choiceManagers_num == 2:                           
        with st.expander("Managers with most home wins / away wins",expanded=True):
            home_away_managers="""SELECT X.id, X.manager_name, X.team, X.homeWins, Y.awayWins
                                    FROM
                                    (
                                        SELECT HM.id, HM.name manager_name, H.name team,
                                        SUM(CASE WHEN M.h_score > M.a_score THEN 1 ELSE 0 END) homeWins
                                        FROM Matches_Held_at M 
                                        INNER JOIN Teams_Owner_Managed_Located H
                                        ON M.team1_id = H.id
                                        INNER JOIN Managers HM
                                        ON H.manager_id = HM.id
                                        GROUP BY HM.id, manager_name, team
                                    ) X
                                    LEFT OUTER JOIN
                                    (
                                        SELECT AM.id, AM.name manager_name, A.name team,
                                        SUM(CASE WHEN M.h_score < M.a_score THEN 1 ELSE 0 END) awayWins
                                        FROM Matches_Held_at M 
                                        INNER JOIN Teams_Owner_Managed_Located A
                                        ON M.team2_id = A.id
                                        INNER JOIN Managers AM
                                        ON A.manager_id = AM.id
                                        GROUP BY AM.id, manager_name, team
                                    ) Y
                                    ON X.id = Y.id
                                    AND X.manager_name = Y.manager_name
                                    AND X.team = Y.team
                                    ORDER BY X.homeWins DESC, Y.awayWins DESC;"""
            result = query_db(home_away_managers)
            st.dataframe(result)
        
elif choice == "Stadiums":
    st.subheader("Stadiums")
    menuStadiums = [
                'Stadiums With Most Goals Scored',
                'Stadiums With Max Home Wins',
                'Stadiums With Max Away Wins'
            ]
    choiceStadiums = st.selectbox("Menu", menuStadiums)
    choiceStadiums_num = menuStadiums.index(choiceStadiums)

    if choiceStadiums_num == 0:                           
        with st.expander("Stadiums With Most Goals Scored",expanded=True):
            goals_stadiums="""SELECT St.name stadium_name, T.name team, 
                                SUM(M.h_score) home_goals, SUM(M.a_score) away_goals, SUM(M.h_score + M.a_score) total_goals_scored
                                FROM Matches_Held_at M
                                INNER JOIN Stadiums St
                                ON M.stadium_id = St.id
                                INNER JOIN Teams_Owner_Managed_Located T
                                ON M.team1_id = T.id
                                GROUP BY St.id, St.name, T.name
                                ORDER BY total_goals_scored DESC;"""
            st.dataframe(query_db(goals_stadiums))

    if choiceStadiums_num == 1:                           
        with st.expander("Stadiums With Max Home Wins",expanded=True):
            home_wins_stadium="""SELECT St.name stadium_name, T.name team,
                                    100*ROUND(SUM(CASE WHEN M.h_score > M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) homeWinPercentage,
                                    100*ROUND(SUM(CASE WHEN M.h_score < M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) homeLossPercentage,
                                    100*ROUND(SUM(CASE WHEN M.h_score = M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) homeDrawPercentage
                                    FROM Matches_Held_at M
                                    INNER JOIN Stadiums St
                                    ON M.stadium_id = St.id
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON M.team1_id = T.id
                                    GROUP BY St.id, St.name, T.name
                                    ORDER BY homeWinPercentage DESC;"""
            result = query_db(home_wins_stadium)
            st.dataframe(result.style.format({"homeWinPercentage": "{:.2f}", "homeLossPercentage": "{:.2f}", "homeDrawPercentage": "{:.2f}"}))

    if choiceStadiums_num == 2:                           
        with st.expander("Stadiums With Max Away Wins",expanded=True):
            away_wins_stadium="""SELECT St.name stadium_name, T.name team,
                                    100*ROUND(SUM(CASE WHEN M.h_score < M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) awayWinPercentage,
                                    100*ROUND(SUM(CASE WHEN M.h_score > M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) awayLossPercentage,
                                    100*ROUND(SUM(CASE WHEN M.h_score = M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) awayDrawPercentage
                                    FROM Matches_Held_at M
                                    INNER JOIN Stadiums St
                                    ON M.stadium_id = St.id
                                    INNER JOIN Teams_Owner_Managed_Located T
                                    ON M.team1_id = T.id
                                    GROUP BY St.id, St.name, T.name
                                    ORDER BY awayWinPercentage DESC;"""
            result = query_db(away_wins_stadium)
            st.dataframe(result.style.format({"awayWinPercentage": "{:.2f}", "awayLossPercentage": "{:.2f}", "awayDrawPercentage": "{:.2f}"}))

elif choice == "Referees":
    st.subheader("Referees")
    menuReferees = [
                'Referees With Most Home Win Percentage',
                'Referees With Most Penalties Awarded',
                'Distribution of Home Teams Officiated By Referees'
            ]
    choiceReferees = st.selectbox("Menu", menuReferees)
    choiceReferees_num = menuReferees.index(choiceReferees)

    if choiceReferees_num == 0:                           
        with st.expander("Referees With Most Home Win Percentage",expanded=True):
            home_wins_referees="""SELECT R.name referee_name, R.nationality, COUNT(M.id) numMatches,
                                    100*ROUND(SUM(CASE WHEN M.h_score > M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) homeWinPercentage,
                                    100*ROUND(SUM(CASE WHEN M.h_score < M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) homeLossPercentage,
                                    100*ROUND(SUM(CASE WHEN M.h_score = M.a_score THEN 1.0 ELSE 0.0 END)/CAST(COUNT(M.id) AS decimal), 4) homeDrawPercentage
                                    FROM Matches_Held_at M
                                    INNER JOIN Officiated_by OB 
                                    ON M.id = OB.match_id
                                    INNER JOIN Referees R
                                    ON OB.referee_id = R.id
                                    GROUP BY R.id, R.name, R.nationality
                                    ORDER BY homeWinPercentage DESC;"""
            result = query_db(home_wins_referees)
            st.dataframe(result.style.format({"homeWinPercentage": "{:.2f}", "homeLossPercentage": "{:.2f}", "homeDrawPercentage": "{:.2f}"}))

    if choiceReferees_num == 1:                           
        with st.expander("Referees With Most Penalties Awarded",expanded=True):
            penalties_referees="""SELECT R.name referee_name, COUNT(DISTINCT OB.match_id) numMatches, 
                                    SUM(CASE WHEN G.pen THEN 1 ELSE 0 END) numPenalties,
                                    100*ROUND(SUM(CASE WHEN G.pen THEN 1.0 ELSE 0.0 END)/CAST(COUNT(DISTINCT OB.match_id) AS decimal), 4) numPenaltiesPercentage
                                    FROM Goals_Scored G
                                    INNER JOIN Officiated_by OB
                                    ON G.match_id = OB.match_id
                                    INNER JOIN Referees R
                                    ON OB.referee_id = R.id
                                    GROUP BY R.id, R.name, R.nationality
                                    ORDER BY numPenaltiesPercentage DESC;"""
            result = query_db(penalties_referees)
            st.table(result.style.format({"numPenaltiesPercentage": "{:.2f}"}))

    if choiceReferees_num == 2:
        sql = "SELECT name FROM referees;"
        try:
            all_referee_names = query_db(sql)["name"].tolist()
            referee_name = st.selectbox("Select A Referee", all_referee_names)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")

        with st.expander("Distribution of Home Teams Officiated By Referees",expanded=True):
            teams_referees=f"""SELECT H.name HomeTeam, COUNT(M.id) cntMatch,
                                SUM(CASE WHEN M.h_score > M.a_score THEN 1 ELSE 0 END) homeWins,
                                SUM(CASE WHEN M.h_score < M.a_score THEN 1 ELSE 0 END) homeLosses,
                                SUM(CASE WHEN M.h_score = M.a_score THEN 1 ELSE 0 END) homeDraws
                                FROM Matches_Held_at M
                                INNER JOIN Officiated_by OB
                                ON M.id = OB.match_id
                                INNER JOIN Referees R
                                ON OB.referee_id = R.id
                                INNER JOIN Teams_Owner_Managed_Located H
                                ON M.team1_id = H.id
                                WHERE R.name = '{referee_name}'
                                GROUP BY R.Name, H.name
                                ORDER BY cntMatch DESC;"""
            result = query_db(teams_referees)
            st.table(result)