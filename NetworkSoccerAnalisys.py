# ----------------------------------------- Network analysis of soccer games -----------------------------------------------
# -Import useful libraries
import json
import networkx as nx
import numpy as np
import csv

#-Import data from json files
team1 = json.load(open("c:/Users/Cedric_'tJampens/Desktop/UGent 2016-2018/jaar 1/Project netwerken/Real Madrid.json", encoding="utf8"))
team2 = json.load(open("c:/Users/Cedric_'tJampens/Desktop/UGent 2016-2018/jaar 1/Project netwerken/barcelona.json", encoding="utf8"))
data = json.load(open("c:/Users/Cedric_'tJampens/Desktop/UGent 2016-2018/jaar 1/Project netwerken/12.RM-B0-4.json", encoding="utf8"))
type_id = json.load(open("c:/Users/Cedric_'tJampens/Desktop/UGent 2016-2018/jaar 1/Project netwerken/type_id.json", encoding="utf8"))
formations = json.load(open("c:/Users/Cedric_'tJampens/Desktop/UGent 2016-2018/jaar 1/Project netwerken/Formation.json", encoding="utf8"))

#-Parameters
BigM = float("inf")
event_count = len(data["Games"]["Game"]["Event"])-1
end_game_time = 0

#-Name of teams
name_team1 = team1["SeasonStatistics"]["Team"]["@attributes"]["name"]
name_team2 = team2["SeasonStatistics"]["Team"]["@attributes"]["name"]

#-ID of teams
team1ID = int(data["Games"]["Game"]["@attributes"]["home_team_id"])
team2ID = int(data["Games"]["Game"]["@attributes"]["away_team_id"])

#-Name of players
player_name1 = []
player_name2 = []

#-Shirtnumbers of players
player_shirtnumber1 = []
player_shirtnumber2 = []

#-Incoming, outgoing and minute of substitution
IN1 = []
IN2 = []
OUT1 = []
OUT2 = []
SUBTIME1 = [0]
SUBTIME2 = [0]

#-Formations of teams
formationindexhome = []
formationindexaway= []

#-Formation coordinates of teams (x and y)
coxhome = []
coyhome = []
coxaway = []
coyaway = []

#-------------------- Start program -------------------------------
#------- Going through all events that happened during a game -----
for i in range(0,len(data["Games"]["Game"]["Event"])):
    event = int(data["Games"]["Game"]["Event"][i]["@attributes"]["type_id"])
    eventID = int(data["Games"]["Game"]["Event"][i]["@attributes"]["event_id"])
    teamID = int(data["Games"]["Game"]["Event"][i]["@attributes"]["team_id"])
    playerID = int(data["Games"]["Game"]["Event"][i]["@attributes"]["player_id"])
    time_event = data["Games"]["Game"]["Event"][i]["@attributes"]["min"]
    end_game_time = max(end_game_time,time_event)

    # ---- event 34 = team formation/selection/shirtnumbers/playerID's
    if event == 34:
        # ---- Going through all qualifiers of this event --
        for j in range(0,len(data["Games"]["Game"]["Event"][i]["Q"])):
            # ---- qualifier 30 = team ID ----
            if int(data["Games"]["Game"]["Event"][i]["Q"][j]["@attributes"]["qualifier_id"]) == 30:

                # Team1 = home team
                if teamID == team1ID:
                    # Create array with all players who are involved in this game: starting 11 + bench
                    selection1 = []
                    selection1 = data['Games']['Game']['Event'][i]['Q'][j]['@attributes']['value'].split(", ")
                    # Create array with the starting 11 players
                    playing1 = selection1[0:11]
                    # Create empty passing and adjacency matrix of 11x11
                    pass_matrix1 = [[0 for i in range(len(playing1))] for j in range(len(playing1))]
                    adjacency1 = [[0 for i in range(len(playing1))] for j in range(len(playing1))]

                    # Get from player ID's their corresponding Shirtnumbers and names
                    for k in range(0, len(playing1)):
                        # Going through the player database from a specific season
                        for m in range(0, len(team1["SeasonStatistics"]["Team"]["Player"])):
                            # If the ID from one of the playing 11 matches the one from the database; their corresponding number and name are extracted
                            if int(playing1[k]) == int(team1["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["player_id"]):
                                player_name1.append(team1["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["nameObj"]["full"])
                                player_shirtnumber1.append(team1["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["shirtNumber"])

                # Team2 = away team
                if teamID == team2ID:
                    # Create array with all players who are involved in this game: starting 11 + bench
                    selection2 = []
                    selection2 = data['Games']['Game']['Event'][i]['Q'][j]['@attributes']['value'].split(", ")
                    # Create array with the starting 11 players
                    playing2 = selection2[0:11]
                    # Create empty passing and adjacency matrix of 11x11
                    pass_matrix2 = [[0 for i in range(len(playing2))] for j in range(len(playing2))]
                    adjacency2 = [[0 for i in range(len(playing2))] for j in range(len(playing2))]

                    # Get from player ID's their corresponding Shirtnumbers and names
                    for k in range(0, len(playing2)):
                        # Going through the player database from a specific season
                        for m in range(0, len(team2["SeasonStatistics"]["Team"]["Player"])):
                            # If the ID from one of the playing 11 matches the one from the database; their corresponding number and name are extracted
                            if int(playing2[k]) == int(team2["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["player_id"]):
                                player_name2.append(team2["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["nameObj"]["full"])
                                player_shirtnumber2.append(team2["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["shirtNumber"])

            # ---- Qualifier 130 = Team formation team 1 ----
            if int(data["Games"]["Game"]["Event"][i]["Q"][j]["@attributes"]["qualifier_id"]) == 130 and int(data["Games"]["Game"]["Event"][i]["@attributes"]["team_id"]) == team1ID:
                formationindexhome.append(str(int(data["Games"]["Game"]["Event"][i]["Q"][j]["@attributes"]["value"]) - 1))  # make array with formation indexes
                formationhome = formations["Team formation"][formationindexhome[0]]["formation"]

                # Get the corresponding X and Y coordinates for every position in the corresponding team formation
                for p in range(1, 12):
                    pos = "pos" + str(p)
                    coxhome.append(int(formations["Team formation"][formationindexhome[0]][pos]["x"]) / 5)  # x-coordinates home team '/5' for scaling purposes
                    coyhome.append(int(formations["Team formation"][formationindexhome[0]][pos]["y"]) / 5)  # y-coordinates away team '/5' for scaling purposes

            # ---- Qualifier 130 = Team formation team 2 ----
            if int(data["Games"]["Game"]["Event"][i]["Q"][j]["@attributes"]["qualifier_id"]) == 130 and int(data["Games"]["Game"]["Event"][i]["@attributes"]["team_id"]) == team2ID:
                formationindexaway.append(str(int(data["Games"]["Game"]["Event"][i]["Q"][j]["@attributes"]["value"]) - 1))  # make array with formation indexes
                formationaway = formations["Team formation"][formationindexaway[0]]["formation"]

                # Get the corresponding X and Y coordinates for every position in the corresponding team formation
                for p in range(1, 12):
                    pos = "pos" + str(p)
                    coxaway.append(int(formations["Team formation"][formationindexaway[0]][pos]["x"]) / 5)
                    coyaway.append(int(formations["Team formation"][formationindexaway[0]][pos]["y"]) / 5)


    # ----- Event 18 = substitution (player out) AND next event 19 = substitution (player in) OR event = last event ----
    if (event == 18 and int(data["Games"]["Game"]["Event"][i + 1]["@attributes"]["type_id"]) == 19) or (i == event_count):
        # Team 1 OR last event (for both teams)
        if teamID == team1ID or i == event_count:
            # NOT the last event
            if i != event_count:
                OUT1.append(playerID)
                IN1.append(data["Games"]["Game"]["Event"][i + 1]["@attributes"]["player_id"])
                SUBTIME1.append(time_event)

            # Create numpy and networkx form of the pass matrix
            numpy_passes1 = np.asmatrix(data=pass_matrix1, dtype=None)
            passgraph1 = nx.from_numpy_matrix(numpy_passes1)

            # Create distance matrix (11x11) = inverse value of amount of passes between player k and m
            distance_matrix1 = [[0 for x in range(len(playing1))] for y in range(len(playing1))]
            for k in range(len(pass_matrix1)):
                for m in range(len(pass_matrix1)):
                    if pass_matrix1[k][m] != 0:
                        distance_matrix1[k][m] = round(1 / (pass_matrix1[k][m]), 3)
                    else:
                        # No pass between player k and m => distance is infinity
                        if k != m:
                            distance_matrix1[k][m] = BigM
                        else:
                            distance_matrix1[k][m] = 0
            # Create numpy and networkx form of the distance matrix
            numpy_distance1 = np.asmatrix(data=distance_matrix1, dtype=None)
            Graph1 = nx.from_numpy_matrix(numpy_distance1)

            # Performing a DIJKSTRA algorithm on the distance matrix to get the shortest path from each player to another player
            path1 = nx.all_pairs_dijkstra_path_length(Graph1)
            pathkey1 = list(path1.keys())
            pathvalue1 = list(path1.items())

            # Initialize metrics:
                # ----- Vertex degree -----
            vertexin1 = [0 for i in range(len(playing1))]
            vertexout1 = [0 for i in range(len(playing1))]
            vertexdegree1 = [0 for i in range(len(playing1))]
             # ----- Radius, diameter and eccentricity -----
            radius1 = 0
            diameter1 = 0
            eccentricity1 = [0 for i in range(0,len(playing1))]
                # ----- Closeness centrality -----
            totalpass1 = 0
            passheader1 = []
            passdistances1 = [0 for x in range(0, len(playing1))]
            Closeness1 = []
                # ----- Betweenness centrality -----
            predecessors1 = [0 for x in range(0, len(playing1))]
            betweenness1 = []
                # ----- Pagerank centrality -----
            PRcentrality1 = []
                # ----- Clustering coefficient -----
            Clust1 = [0 for x in range(0, len(playing1))]
            Clust_avg_team1 = 0
            MaxPasses1 = 0
            totvar1 = 0

            # ---------- Calculate metrics ----------
                # Create a shortest distance matrix out of the shortest path dictionary previously calculated in path1:
            shortestdistancematrix1 = [[BigM for i in range(len(playing1))] for j in range(len(playing1))]

                # Calculate the vertex degrees, radius, diameter and eccentricity of team 1:
            for k in range(0, len(pathkey1)):
                locvar1 = 0
                for m in range(0, len(pathkey1)):
                    shortestdistancematrix1[k][m] = round(pathvalue1[k][1][m], 3)
                    MaxPasses1 = max(MaxPasses1,pass_matrix1[k][m])
                    if pass_matrix1[k][m] != 0:
                        locvar1 += 1
                    if adjacency1[k][m] == 1:
                        vertexout1[k] += 1
                        vertexdegree1[k] += 1
                    if adjacency1[m][k] == 1:
                        vertexin1[k] += 1
                        vertexdegree1[k] += 1
                if locvar1 > 0:
                    totvar1 += 1
            if totvar1 == int(len(playing1)):
                radius1 = nx.radius(passgraph1)
                diameter1 = nx.diameter(passgraph1)
                eccentricity1 = nx.eccentricity(passgraph1)
            if totvar1 != int(len(playing1)):
                radius1 = "NaN"
                diameter1 = "NaN"
                eccentricity1 = ["NaN" for i in range(0,len(playing1))]

                # Calculate the closeness centrality and clustering coefficient:
            # 'a' as between node
            for a in range(0, len(playing1)):
                locvar = 0
                dij = 0.0
                dji = 0.0

                # 'b' as source node
                for b in range(0, len(playing1)):
                    if shortestdistancematrix1[a][b] != BigM and a != b:
                        locvar += 1
                        dij += shortestdistancematrix1[a][b]
                    if shortestdistancematrix1[b][a] != BigM and a != b:
                        locvar += 1
                        dji += shortestdistancematrix1[b][a]

                    # Where source node 'b' is not equal to between node 'a'
                    if b != a:
                        totalpath1 = nx.dijkstra_predecessor_and_distance(Graph1, source=b)
                        # 'k' as target node
                        for k in range(0, len(playing1)):

                            # Where source node 'b' is not equal to between node 'a' and not to target node 'k' and the path is not equal to infinity
                            if k != b and k != a and shortestdistancematrix1[b][k] != BigM:
                                for m in range(0, len(totalpath1[0][k])):
                                    if totalpath1[0][k][m] == a:
                                        predecessors1[a] += 1
                                Clust1[a] += pow((pass_matrix1[a][b]/MaxPasses1)*(pass_matrix1[k][b]/MaxPasses1)*(pass_matrix1[k][a]/MaxPasses1),1/3)

                if vertexout1[a] >= 2:
                    Clust1[a] = round(Clust1[a]/(vertexout1[a]*(vertexout1[a]-1)),3)
                if vertexout1[a] < 2:
                    Clust1[a] = 0
                Clust_avg_team1 += Clust1[a]/int(len(playing1))
                Clust_avg_team1 = round(Clust_avg_team1,3)

                if locvar >= 1:
                    totalpass1 += 1
                    totald = round(dij + dji, 2)
                    passdistances1[a] = totald

            # ----- Closeness, Betweenness and Pagerank centrality of team 1 -----
            Pagerank1 = nx.pagerank(passgraph1, alpha=0.85, max_iter=100, tol=1.0e-6, weight='weight', nstart=None, dangling=None)
            for a in range(0, len(playing1)):
                # CC(u)
                if passdistances1[a] != 0:
                    Closeness1.append(round(2 * (totalpass1 - 1) / passdistances1[a], 3))
                if passdistances1[a] == 0:
                    Closeness1.append(0.00)
                # CB(u)
                betweenness1.append(round(predecessors1[a] / ((len(playing1) - 1) * (len(playing1) - 2)), 3))
                # P(u)
                PRcentrality1.append(round(Pagerank1[a], 3))
            # ---------- End of metrics ----------

            # ---------- Total metric array team 1 ----------
                # Events before the end of the game:
            if i != event_count:
                print("\n----------------------------------------------------------------------\nGame time: ",SUBTIME1[len(SUBTIME1)-2], " - " ,time_event," minutes\n\nTeam 1 overview:\naverage clustering coefficient:", Clust_avg_team1,"\nradius:",radius1,"\ndiameter:",diameter1,"\n")
                phase_nodes1 = 'team1_minute_' + str(time_event) + '_nodes.csv'
                phase_edges1 = 'team1_minute_' + str(time_event) + '_edges.csv'
                phase_metrics1 = 'team1_minute_' + str(time_event) + '_metrics.csv'

                # Event to end the game:
            if i == event_count:
                print("\n----------------------------------------------------------------------\nEnd time: ",SUBTIME1[len(SUBTIME1)-1], " - ", end_game_time, " minutes\n\nTeam 1 overview:\naverage clustering coefficient:", Clust_avg_team1,"\nradius:",radius1,"\ndiameter:",diameter1,"\n")
                phase_nodes1 = 'team1_minute_' + str(end_game_time) + '_nodes.csv'
                phase_edges1 = 'team1_minute_' + str(end_game_time) + '_edges.csv'
                phase_metrics1 = 'team1_minute_' + str(end_game_time) + '_metrics.csv'

                # Total array team 1:
            Total1 = [['shirtnumber', 'Player','player degree in', 'player degree out', 'total player degree','Eccentricity','Closeness centrality', 'Betweenness centrality','Clustering', 'Pagerank centrality']]
            print(Total1[0])
            for x in range(1, len(playing1) + 1):
                Total1.append([player_shirtnumber1[x - 1], player_name1[x - 1], vertexin1[x-1],vertexout1[x-1],vertexdegree1[x-1],eccentricity1[x-1] ,Closeness1[x - 1], betweenness1[x - 1],Clust1[x-1] ,PRcentrality1[x - 1]])
                print(Total1[x])
            print("----------------------------------------------------------------------\n")
            # ---------- End of total array ---------

            # ---------- Exporting CSV files for gephi ----------
                # Create array with all player nodes of team 1 with corresponding attributes:
            nodes1 = [[player_shirtnumber1[y], player_name1[y], coxhome[y], coyhome[y]] for y in range(len(playing1))]
            nodes1.insert(0, ['Id', 'Label', 'x-coordinate', 'y-coordinate'])

                # Create array with all player edges of team 1 with corresponding attributes:
            edges1 = [['Source', 'Target', 'Weight']]
            for k in range(len(pass_matrix1)):
                for m in range(len(pass_matrix1)):
                    if pass_matrix1[k][m] > 0:
                        source_player = player_shirtnumber1[k]
                        target_player = player_shirtnumber1[m]
                        weight = pass_matrix1[k][m]
                        edges1.append([source_player, target_player, weight])

                # Create and write CSV files:
            with open(phase_nodes1, 'w', newline='') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(nodes1)

            with open(phase_edges1, 'w', newline='') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(edges1)

            with open(phase_metrics1, 'w', newline = '') as fp:
                a = csv.writer(fp, delimiter = ',')
                a.writerows(Total1)
            # ---------- End exporting CSV files ----------

            # ----- Initializing team 1 after substitute -----
            for k in range(0, len(playing1)):
                if int(playing1[k]) == playerID:
                    playing1[k] = data["Games"]["Game"]["Event"][i + 1]["@attributes"]["player_id"]

                    for m in range(0, len(team1["SeasonStatistics"]["Team"]["Player"])):
                        if int(playing1[k]) == int(team1["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["player_id"]):
                            player_name1[k] = team1["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["nameObj"]["full"]
                            player_shirtnumber1[k] = int(team1["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["shirtNumber"])

            pass_matrix1 = [[0 for i in range(len(playing1))] for j in range(len(playing1))]
            adjacency1 = [[0 for i in range(len(playing1))] for j in range(len(playing1))]
        # ---------- End Team 1 ----------


        # Team 2 OR last event (for both teams)
        if teamID == team2ID or i == event_count:
            # NOT the last event
            if i != event_count:
                OUT2.append(playerID)
                IN2.append(data["Games"]["Game"]["Event"][i + 1]["@attributes"]["player_id"])
                SUBTIME2.append(time_event)

            # Create numpy and networkx form of the pass matrix
            numpy_passes2 = np.asmatrix(data=pass_matrix2, dtype=None)
            passgraph2 = nx.from_numpy_matrix(numpy_passes2)

            # Create distance matrix (11x11) = inverse value of amount of passes between player k and m
            distance_matrix2 = [[0 for x in range(len(playing2))] for y in range(len(playing2))]
            for k in range(len(pass_matrix2)):
                for m in range(len(pass_matrix2)):
                    if pass_matrix2[k][m] != 0:
                        distance_matrix2[k][m] = round(1 / (pass_matrix2[k][m]), 3)
                    else:
                        # No pass betweenplayer k and m => distance is infinity
                        if k != m:
                            distance_matrix2[k][m] = BigM
                        else:
                            distance_matrix2[k][m] = 0
            # Create numpy and networkx form of the distance matrix
            numpy_distance2 = np.asmatrix(data=distance_matrix2, dtype=None)
            Graph2 = nx.from_numpy_matrix(numpy_distance2)

            # Performing a DIJKSTRA algorithm on the distance matrix to get the shortest path from each player to another player
            path2 = nx.all_pairs_dijkstra_path_length(Graph2)  # pathlength
            pathkey2 = list(path2.keys())
            pathvalue2 = list(path2.items())

            # Initialize metrics:
                # ----- Vertex degree -----
            vertexin2 = [0 for i in range(len(playing2))]
            vertexout2 = [0 for i in range(len(playing2))]
            vertexdegree2 = [0 for i in range(len(playing2))]
                # ----- Radius, diameter and eccentricity -----
            radius2 = 0
            diameter2 = 0
            eccentricity2= [0 for i in range(0, len(playing2))]
                # ----- Closeness centrality -----
            totalpass2 = 0
            passheader2 = []
            passdistances2 = [0 for x in range(0, len(playing2))]
            Closeness2 = []
                # ----- Betweenness centrality -----
            predecessors2 = [0 for x in range(0, len(playing2))]
            betweenness2 = []
                # ----- Pagerank centrality -----
            PRcentrality2 = []
                # ----- Clustering coefficient -----
            Clust2 = [0 for x in range(0, len(playing2))]
            Clust_avg_team2 = 0
            MaxPasses2 = 0
            totvar2 = 0

            # ---------- Calculate metrics ----------
                # Create a shortest distance matrix out of the shortest path dictionary prviously calculated in path 2:
            shortestdistancematrix2 = [[BigM for i in range(len(playing2))] for j in range(len(playing2))]

                # Calculate the vertex degrees, radius, diameter and eccentricity of team 2:
            for k in range(0, len(pathkey2)):
                locvar2 = 0
                for m in range(0, len(pathkey2)):
                    shortestdistancematrix2[k][m] = round(pathvalue2[k][1][m], 3)
                    MaxPasses2 = max(MaxPasses2, pass_matrix2[k][m])
                    if pass_matrix2[k][m] != 0:
                        locvar2 += 1
                    if adjacency2[k][m] == 1:
                        vertexout2[k] += 1
                        vertexdegree2[k] += 1
                    if adjacency2[m][k] == 1:
                        vertexin2[k] += 1
                        vertexdegree2[k] += 1
                if locvar2 > 0:
                    totvar2 += 1
            if totvar2 == int(len(playing2)):
                radius2 = nx.radius(passgraph2)
                diameter2 = nx.diameter(passgraph2)
                eccentricity2 = nx.eccentricity(passgraph2)
            if totvar2 != int(len(playing1)):
                radius2 = "NaN"
                diameter2 = "NaN"
                eccentricity2 = ["NaN" for i in range(0, len(playing2))]

                # Calculate the closeness centrality and clustering coefficient:
            # 'a' as between node
            for a in range(0, len(playing2)):
                locvar = 0
                dij = 0.0
                dji = 0.0

                # 'b' as source node
                for b in range(0, len(playing2)):
                    if shortestdistancematrix2[a][b] != BigM and a != b:
                        locvar += 1
                        dij += shortestdistancematrix2[a][b]
                    if shortestdistancematrix2[b][a] != BigM and a != b:
                        locvar += 1
                        dji += shortestdistancematrix2[b][a]

                    # Where source node 'b' is not equal to between node 'a'
                    if b != a:
                        totalpath2 = nx.dijkstra_predecessor_and_distance(Graph2, source=b)
                        # 'k' as target node
                        for k in range(0, len(playing2)):

                            # Where source node 'b' is not equal to between node 'a' and not to target node 'k'
                            if k != b and k != a and shortestdistancematrix2[b][k] != BigM:
                                for m in range(0, len(totalpath2[0][k])):
                                    if totalpath2[0][k][m] == a:
                                        predecessors2[a] += 1
                            Clust2[a] += pow((pass_matrix2[a][b] / MaxPasses2) * (pass_matrix2[k][b] / MaxPasses2) * (pass_matrix2[k][a] / MaxPasses2), 1 / 3)

                if vertexout2[a] >= 2:
                    Clust2[a] = round(Clust2[a] / (vertexout2[a] * (vertexout2[a] - 1)), 3)
                if vertexout2[a] < 2:
                    Clust2[a] = 0
                Clust_avg_team2 += Clust2[a] / int(len(playing2))
                Clust_avg_team2 = round(Clust_avg_team2, 3)

                if locvar >= 1:
                    totalpass2 += 1
                    totald = round(dij + dji, 2)
                    passdistances2[a] = totald

            # ----- Closeness, Betweenness and Pagerank centrality of team 2 -----
            Pagerank2 = nx.pagerank(passgraph2, alpha=0.85, max_iter=100, tol=1.0e-6, weight='weight', nstart=None,dangling=None)
            for a in range(0, len(playing2)):
                # CC(u)
                if passdistances2[a] != 0:
                    Closeness2.append(round(2 * (totalpass2 - 1) / passdistances2[a], 2))
                if passdistances2[a] == 0:
                    Closeness2.append(0.00)
                # CB(u)
                betweenness2.append(round(predecessors2[a] / ((len(playing2) - 1) * (len(playing2) - 2)), 3))
                # P(u)
                PRcentrality2.append(round(Pagerank2[a], 3))
            # ---------- End of metrics ----------

            # ----------- Total metric array team 2 -----------
                # Events before the end of the game:
            if i != event_count:
                print("\n----------------------------------------------------------------------\nGame time: ", SUBTIME2[len(SUBTIME2)-2], " - ",time_event, " minutes\n\nTeam 2 overview:\naverage clustering coefficient:", Clust_avg_team2,"\nradius:",radius2,"\ndiameter:",diameter2,"\n")
                phase_nodes2 = 'team2_minute_' + str(time_event) + '_nodes.csv'
                phase_edges2 = 'team2_minute_' + str(time_event) + '_edges.csv'
                phase_metrics2 = 'team2_minute_' + str(time_event) + '_metrics.csv'

                # Event to end the game:
            if i == event_count:
                print("\n----------------------------------------------------------------------\nEnd time: ", SUBTIME2[len(SUBTIME2)-1], " - ", end_game_time, " minutes\n\nTeam 2 overview:\naverage clustering coefficient:", Clust_avg_team2,"\nradius:",radius2,"\ndiameter:",diameter2,"\n")
                phase_nodes2 = 'team2_minute_' + str(end_game_time) + '_nodes.csv'
                phase_edges2 = 'team2_minute_' + str(end_game_time) + '_edges.csv'
                phase_metrics2 = 'team2_minute_' + str(end_game_time) + '_metrics.csv'

                # Total array team 2:
            Total2 = [['shirtnumber', 'Player', 'player degree in', 'player degree out', 'total player degree','Eccentricity', 'Closeness centrality', 'Betweenness centrality','Clustering','Pagerank centrality']]
            print(Total2[0])
            for x in range(1, len(playing2) + 1):
                Total2.append([player_shirtnumber2[x - 1], player_name2[x - 1], vertexin2[x-1], vertexout2[x-1], vertexdegree2[x-1],eccentricity2[x-1],Closeness2[x - 1], betweenness2[x - 1],Clust2[x-1],PRcentrality2[x - 1]])
                print(Total2[x])
            print("----------------------------------------------------------------------\n")
            # ----------- End of total array ----------

            # ----------- Exporting CSV files for gephi ----------
                # Create array with all player nodes of team 2 with corresponding attributes:
            nodes2 = [[player_shirtnumber2[y], player_name2[y], coxaway[y], coyaway[y]] for y in range(len(playing2))]
            nodes2.insert(0, ['Id', 'Label', 'x-coordinate', 'y-coordinate'])

                # Create array with all player edges of team 2 with corresponding attributes:
            edges2 = [['Source', 'Target', 'Weight']]
            for k in range(len(pass_matrix2)):
                for m in range(len(pass_matrix2)):
                    if pass_matrix2[k][m] > 0:
                        source_player = player_shirtnumber2[k]
                        target_player = player_shirtnumber2[m]
                        weight = pass_matrix2[k][m]
                        edges2.append([source_player, target_player, weight])

                # Create and write CSV files:
            with open(phase_nodes2, 'w', newline='') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(nodes2)

            with open(phase_edges2, 'w', newline='') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(edges2)

            with open (phase_metrics2, 'w' , newline = '') as fp:
                a = csv.writer(fp, delimiter = ',')
                a.writerows(Total2)
            # --------- End exporting CSV files ----------

            # ----- Initializing team 2 after substitute -----
            for k in range(0, len(playing2)):
                if int(playing2[k]) == playerID:
                    playing2[k] = data["Games"]["Game"]["Event"][i + 1]["@attributes"]["player_id"]

                    for m in range(0, len(team2["SeasonStatistics"]["Team"]["Player"])):
                        if int(playing2[k]) == int(team2["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["player_id"]):
                            player_name2[k] = team2["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["nameObj"]["full"]
                            player_shirtnumber2[k] = int(team2["SeasonStatistics"]["Team"]["Player"][m]["@attributes"]["shirtNumber"])

            pass_matrix2 = [[0 for i in range(len(playing2))] for j in range(len(playing2))]
            adjacency2 = [[0 for i in range(len(playing2))] for j in range(len(playing2))]
        # ---------- End Team 2 ----------
    # ----- End of calculations ------

    # ----- Event 1 = pass given -----
    if event == 1:

        receiving_player = ""
        name_player = ""

        I = 0
        J = 0

        # The player receiving the pass is the sequential event + the outcome has to be 1 = pass is well sent
        receiving_playerID = int(data["Games"]["Game"]["Event"][i + 1]["@attributes"]["player_id"])
        if int(data["Games"]["Game"]["Event"][i]["@attributes"]["outcome"]) == 1 and \
                        teamID == int(data["Games"]["Game"]["Event"][i+1]["@attributes"]["team_id"]) and \
                        playerID != int(data["Games"]["Game"]["Event"][i+1]["@attributes"]["player_id"]):  # successful pass

            # ----- team 1: filling in the passmatrix and adjacency matrix-----
            if teamID == team1ID:
                for kk in range(0, len(playing1)):

                    if playerID == int(playing1[kk]):
                        name_player = player_name1[kk]
                        I = int(kk)

                    if receiving_playerID == int(playing1[kk]):
                        receiving_player = player_name1[kk]
                        J = int(kk)

                pass_matrix1[I][J] += 1

                if adjacency1[I][J] == 0:
                    adjacency1[I][J] = 1
                #print(str(i),name_team1+":",str(name_player),"to",receiving_player,"I:",I,"J:",J)

            # ----- team 2: filling in the passmatrix and adjacency matrix -----
            if teamID == team2ID:
                for jj in range(0,len(playing2)):

                    if playerID == int(playing2[jj]):
                        name_player = player_name2[jj]
                        I = int(jj)

                    if receiving_playerID == int(playing2[jj]):
                        receiving_player = player_name2[jj]
                        J = int(jj)

                pass_matrix2[I][J] += 1

                if adjacency2[I][J] == 0:
                    adjacency2[I][J] = 1
                #print(str(i),name_team2+":",str(name_player),"->",receiving_player,"I:",I,"J:",J)

        receiving_player = ""
        name_player = ""
    # ----- End of event 1 -----
# End of event - loop
# End of program

