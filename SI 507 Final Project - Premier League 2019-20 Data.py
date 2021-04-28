#!/usr/bin/env python
# coding: utf-8

# # SI 507 Final Project - Premier League 2019-20 Data
# ### By Yash Kamat
# ---

# ## Preprocessing

# ### Imports

# In[1]:


# Global Import
import warnings
warnings.filterwarnings('ignore')

# Data Processing Packages
import numpy               as np
import pandas              as pd

# API/Caching Packages
import requests
import json
import sqlite3
import secrets as secrets

#Data Visualization Packages
import plotly.graph_objs as go
import plotly.express as px


# ### Function Definition

# In[2]:


def get_player_api(name:str):
    '''Return a dictionary instance of a player's API data.
    
    Parameters
    ----------
    name: string
        Name of the player.
    
    Returns
    -------
    dict
        Dictionary instance of a player's API data.
    '''
    if name in curr_cache.keys():
        print('Using cache\n')
        api_result = curr_cache[name]
        return(api_result)

    else:
        print('Using API\n')
        f_name = name.split()[0]
        s_name = name.replace(f_name + " ","")
        
        url = "https://v3.football.api-sports.io/players"

        query={'league':39, 'search':s_name}
        headers = {
          'x-apisports-key': secrets.API_KEY,
        }

        response = requests.request("GET", url, headers=headers, params=query)
        response_text = json.loads(response.text)
        
        if response_text['results'] > 1:
            for player in response_text['response']:
                if player['player']['name'] == f'{name[0]}. {s_name}' or player['player']['name'] == name:
                    api_result = {name:player}
                    
        else:
            api_result = {name:response_text['response'][0]}
            
        curr_cache.update(api_result)
        
        with open('api_cache.json', 'w') as json_file:
            json.dump(curr_cache, json_file)
            
        return(api_result[name])


# In[3]:


def at_a_glance(player_dict:dict):
    '''Gives a snapshot look at a player's 2019/20 season statistics.
    
    Parameters
    ----------
    player_dict: dict
        Dictonary instance of a player's API data.
    
    Returns
    -------
    None
    '''
    player_info = player_dict['player']
    club_name = player_dict['statistics'][1]['team']['name']
    season_stats = player_dict['statistics'][1]

    print(f'Name: {player_info["firstname"]+ " " + player_info["lastname"]}\nAge: {player_info["age"]}\nPosition: {season_stats["games"]["position"]}\nCurrent Club: {club_name}\nNationality: {player_info["nationality"]}\n')
    print('2019/20 Stats:\n\n')
    print(f'Appearances: {season_stats["games"]["appearences"]}')
    
    
    if season_stats["games"]["position"]=="Attacker":
        print(f'Goals Scored: {season_stats["goals"]["total"]}')
        print(f'Assists: {season_stats["goals"]["assists"]}')
        print(f'Shot Accuracy: {round(season_stats["shots"]["on"]*100/season_stats["shots"]["total"])}%')
    elif season_stats["games"]["position"]=="Defender":
        print(f'Goals Scored: {season_stats["goals"]["total"]}')
        print(f'Tackles: {season_stats["tackles"]["total"]}')
        print(f'Duel Success Rate: {round(season_stats["duels"]["won"]*100/season_stats["duels"]["total"])}%')
        print(f'Fouls Committed: {season_stats["fouls"]["committed"]}')
    elif season_stats["games"]["position"]=="Midfielder":
        print(f'Goals Scored: {season_stats["goals"]["total"]}')
        print(f'Assists: {season_stats["goals"]["assists"]}')
        print(f'Shot Accuracy: {round(season_stats["shots"]["on"]*100/season_stats["shots"]["total"])}%')
        print(f'Dribble Success Rate: {round(season_stats["dribbles"]["success"]*100/season_stats["dribbles"]["attempts"])}%')
        print(f'Tackles: {season_stats["tackles"]["total"]}')
    else: #Goalkeepers
        print(f'Goals Conceded: {season_stats["goals"]["conceded"]}')
        print(f'Saves: {season_stats["goals"]["saves"]}')
    print(f'Passing Accuracy: {season_stats["passes"]["accuracy"]}%')
    print(f'Cards: Yellow({season_stats["cards"]["yellow"]}) Red({season_stats["cards"]["yellowred"]+season_stats["cards"]["red"]})\n')


# In[4]:


def line_ind(player_name:str, metric:str):
    '''Presents a line graph for an individual player.
    
    Parameters
    ----------
    player_name: string
        The name of the player being searched for.
    
    metric: string
        The metric to be visualized.
        
    Returns
    -------
    None
    '''
    f_name = player_name.split()[0]
    s_name = player_name.replace(f_name + " ","")
    
    fig = px.line(new_sample_data[(new_sample_data['first_name'] == f_name) & (new_sample_data['second_name'] == s_name)],
                  x='round', y=metric,labels=labels_dict,title=f'Week-Wise {labels_dict[metric]} Trend for {player_name}')
    fig.show()


# In[5]:


def scatter_ind(player_name:str, metric1:str, metric2:str):
    '''Presents a scatter graph for an individual player.
    
    Parameters
    ----------
    player_name: string
        The name of the player being searched for.
    
    metric1: string
        The metric to be visualized on the x-axis.
        
    metric2: string
        The metric to be visualized on the y-axis.

    Returns
    -------
    None
    '''
    f_name = player_name.split()[0]
    s_name = player_name.replace(f_name + " ","")
    fig = px.scatter(new_sample_data[(new_sample_data['first_name'] == f_name) & (new_sample_data['second_name'] == s_name)],
               x=metric1, y=metric2, hover_data=['round'], labels=labels_dict, title=f'Scatter Plot: {labels_dict[metric1]} vs {labels_dict[metric2]} Trend for {player_name}')
    fig.show()


# In[6]:


def line_mul(player_name1:str, player_name2:str, metric:str):
    '''Presents a line graph for a pair of players.
    
    Parameters
    ----------
    player_name1: string
        The name of the first player being searched for.

    player_name2: string
        The name of the second player being searched for.
    
    metric: string
        The metric to be visualized.
        
    Returns
    -------
    None
    '''
    
    f_name1 = player_name1.split()[0]
    s_name1 = player_name1.replace(f_name1 + " ","")
    
    f_name2 = player_name2.split()[0]
    s_name2 = player_name2.replace(f_name2 + " ","")
    
    fig = px.line(new_sample_data[((new_sample_data['first_name'] == f_name1) &
                                   (new_sample_data['second_name'] == s_name1))| 
                                  ((new_sample_data['first_name'] == f_name2) &
                                   (new_sample_data['second_name'] == s_name2))], x='round', y=metric,
                  color='second_name', labels=labels_dict,
                  title=f'Week-Wise {labels_dict[metric]} Trend for {player_name1} vs {player_name2}')
    fig.show()


# In[7]:


def bar_mul(player_name1:str, player_name2:str, metric1:str, metric2=None):
    '''Presents either a singular or grouped bar graph for a pair of players.
    
    Parameters
    ----------
    player_name1: string
        The name of the first player being searched for.
    
    player_name2: string
        The name of the second player being searched for.
    
    metric1: string
        The first metric to be visualized.
        
    metric2 (optional): string
        The second metric to be visualized.
    
    Returns
    -------
    None
    '''
    
    f_name1 = player_name1.split()[0]
    s_name1 = player_name1.replace(f_name1 + " ","")
    
    f_name2 = player_name2.split()[0]
    s_name2 = player_name2.replace(f_name2 + " ","")
    if metric2:
        players=[labels_dict[metric1], labels_dict[metric2]]

        fig = go.Figure(data=[go.Bar(name=player_name1,
                                     x=players,
                                     y=[new_sample_data.query("first_name==@f_name1 and second_name==@s_name1")[metric1].sum(),
                                        new_sample_data.query("first_name==@f_name1 and second_name==@s_name1")[metric2].sum()]),
                              go.Bar(name=player_name2,
                                     x=players,
                                     y=[new_sample_data.query("first_name==@f_name2 and second_name==@s_name2")[metric1].sum(),
                                        new_sample_data.query("first_name==@f_name2 and second_name==@s_name2")[metric2].sum()])
        ])

        fig.update_layout(barmode='group')
    else:
        fig = px.bar(x=[player_name1, player_name2],
                     y=[new_sample_data.query("first_name==@f_name1 and second_name==@s_name1")[metric1].sum(),
                        new_sample_data.query("first_name==@f_name2 and second_name==@s_name2")[metric1].sum()],
                     labels={'x':labels_dict[metric1],'y':'Value'},
                     title = f'{player_name1} vs {player_name2}: {labels_dict[metric1]}')
    fig.show()


# In[8]:


def scatter_mul(team:str, week:int, metric1:str, metric2:str):
    '''Presents a scatter graph for an entire team, for a specific gameweek.
    
    Parameters
    ----------
    team: string
        The name of the team being searched for.
        
    week: int
        The game-week number to be visualized.
        
    metric1: string
        The metric to be visualized on the x-axis.
        
    metric2: string
        The metric to be visualized on the y-axis.

    Returns
    -------
    None
    '''
    
    fig = px.scatter(new_sample_data[(new_sample_data['round']==week) & (new_sample_data['team']==team.title())],
                     x=metric1, y=metric2, hover_data=['first_name', 'second_name'], labels=labels_dict,
                     title=f'Week {week} Comparison for {team.title()} ({labels_dict[metric1]} vs {labels_dict[metric2]})')
    fig.show()


# In[9]:


def radar_mul(player_name1:str, player_name2:str, metric_list:list):
    '''Presents a radar graph for a pair of players for 5 metrics.
    
    Parameters
    ----------
    player_name1: string
        The name of the first player being searched for.
        
    player_name2: string
        The name of the second player being searched for.
    
    metric_list: list
        The list of metrics to be visualized.

    Returns
    -------
    None
    '''
    
    go.Figure()

    categories = metric_list

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
          r=[(radar_df[radar_df['name']==player_name1][x]*5/radar_df[x].max()).values[0] for x in categories],
          theta=categories,
          fill='toself',
          name=player_name1))

    fig.add_trace(go.Scatterpolar(
          r=[(radar_df[radar_df['name']==player_name2][x]*5/radar_df[x].max()).values[0] for x in categories],
          theta=categories,
          fill='toself',
          name=player_name2))

    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0, 5])),
                      showlegend=True,
                      title = f'Radar Plot: {player_name1} vs {player_name2}')

    fig.show()


# In[10]:


def select_choice():
    '''Presents a choice of metrics to be visualized.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    '''
    print('\n')
    for k in labels_dict_inv:
        print(f'{list(labels_dict_inv.keys()).index(k)+1}) {k}')
    print('\n')


# In[11]:


def select_team():
    '''Presents a choice of teams from the Premier League.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    print('\n')
    for k in team_dict:
        print(f'{k}) {team_dict[k]}')
    print('\n')


# In[12]:


def user_interface():
    '''Runs the user facing loop to visualize individual/multi- player metrics and comparisons.
    
    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    while True:
        ind_vs_mul = input('Welcome to the Premier League 2019/20 stats visualizer! Which stats would you like to see today?\n1) Individual\n2) Multi-Player Comparison\n3) Exit\n\n')

        if ind_vs_mul == 'exit':
            break
        elif ind_vs_mul.isnumeric():
            if int(ind_vs_mul) == 1:
                while True:
                    ind_choice = input('Please choose one of the following:\n1) At A Glance\n2) Season-long Trend (Line)\n3) Season-long Trend (Scatter)\n4) Back\n\n')

                    if ind_choice.isnumeric():
                        if int(ind_choice) == 1:
                            p_name = input('Player Name: ')
                            print('\n')
                            at_a_glance(get_player_api(p_name))
                        elif int(ind_choice) == 2:
                            p_name = input('Player Name: ')
                            select_choice()
                            metric = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric: '))-1]]
                            line_ind(p_name, metric)
                        elif int(ind_choice) == 3:
                            p_name = input('Player Name: ')
                            select_choice()
                            metric1 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 1: '))-1]]
                            metric2 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 2: '))-1]]
                            scatter_ind(p_name, metric1, metric2)
                        elif int(ind_choice) == 4:
                            break
                        else:
                            print('Error: Invalid Input. Please re-enter your choice.')
                    else:
                        print('Error: Invalid Input. Please re-enter your choice.')
            elif int(ind_vs_mul) == 2:
                while True:
                    mul_choice = input('Please choose one of the following:\n1) Season-long Trend (Line, 2 players)\n2) Gameweek Snapshot for a Team (Scatter)\n3) Single/Two-Metric Comparison (Bar, 2 players)\n4) Five-Metric Comparison (Radar, 2 players)\n5) Back\n\n')

                    if mul_choice.isnumeric():
                        if int(mul_choice) == 1:
                            p_name1 = input('Player 1 Name: ')
                            p_name2 = input('Player 2 Name: ')
                            select_choice()
                            metric = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric: '))-1]]
                            line_mul(p_name1, p_name2, metric)
                        elif int(mul_choice) == 2:
                            select_team()
                            t_name = team_dict[input('Team Name: ')]
                            gw = int(input('Week: '))
                            select_choice()
                            metric1 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 1: '))-1]]
                            metric2 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 2: '))-1]]
                            scatter_mul(t_name, gw, metric1, metric2)
                        elif int(mul_choice) == 3:
                            p_name1 = input('Player 1 Name: ')
                            p_name2 = input('Player 2 Name: ')
                            select_choice()
                            metric1 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 1: '))-1]]
                            metric2 = input('Metric 2 (Optional, press Enter/Return to skip): ')
                            if metric2 == '':
                                bar_mul(p_name1, p_name2, metric1)
                            else:
                                metric2 = labels_dict_inv[list(labels_dict_inv.keys())[int(metric2)-1]]
                                bar_mul(p_name1, p_name2, metric1, metric2)
                        elif int(mul_choice) == 4:
                            metric_list = []
                            p_name1 = input('Player 1 Name: ')
                            p_name2 = input('Player 2 Name: ')
                            select_choice()
                            metric1 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 1: '))-1]]
                            metric2 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 2: '))-1]]
                            metric3 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 3: '))-1]]
                            metric4 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 4: '))-1]]
                            metric5 = labels_dict_inv[list(labels_dict_inv.keys())[int(input('Metric 5: '))-1]]
                            radar_mul(p_name1, p_name2, [metric1, metric2, metric3, metric4, metric5])
                        elif int(mul_choice) == 5:
                            break
                        else:
                            print('Error: Invalid Input. Please re-enter your choice.')
                    else:
                        print('Error: Invalid Input. Please re-enter your choice.')
            elif int(ind_vs_mul) == 3:
                break
            else:
                print('Error: Invalid Input. Please re-enter your choice.')
        else:
            print('Error: Invalid Input. Please re-enter your choice.')


# ### Data Collection and Processing

# In[13]:


with open('api_cache.json', 'r') as json_file:
        curr_cache = json.load(json_file)


# In[14]:


df = pd.read_csv('players_1920_fin.csv')
name_data = pd.read_csv('player_idlist.csv')


# In[15]:


df_vis = df.drop(['Unnamed: 0', 'kickoff_time', 'was_home', 'full', 'bps',
                  'transfers_in', 'transfers_out', 'team_a_score', 'team_h_score'], axis=1)


# In[16]:


new_sample_data = pd.merge(df_vis, name_data, left_on='element', right_on='id')


# In[17]:


new_sample_data = new_sample_data[['id','round','first_name','second_name','team','opponent_team', 'total_points',
                                   'minutes', 'goals_scored', 'assists', 'bonus', 'clean_sheets', 'goals_conceded',
                                   'ict_index', 'own_goals', 'penalties_missed', 'penalties_saved','red_cards',
                                   'saves', 'selected','transfers_balance', 'value', 'yellow_cards', 'ppm']]


# In[18]:


labels_dict = {}
for metric in new_sample_data.columns:
    if "_" in str(metric):
        labels_dict.update({str(metric): str(metric).replace("_", " ").title()})
    elif metric == "ppm":
        labels_dict.update({str(metric): 'Points per Million'})
    elif metric == "ict_index":
        labels_dict.update({str(metric): 'ICT Index'})
    else:
        labels_dict.update({str(metric): str(metric).title()})


# In[19]:


labels_dict_inv = {}
for k in labels_dict:
    labels_dict_inv.update({labels_dict[k]:k})
    
del(labels_dict_inv['Id'])
del(labels_dict_inv['Round'])
del(labels_dict_inv['First Name'])
del(labels_dict_inv['Second Name'])
del(labels_dict_inv['Team'])
del(labels_dict_inv['Opponent Team'])


# In[20]:


team_dict = {}
for i in range(len(new_sample_data['team'].unique())):
    team_dict.update({str(i+1):new_sample_data['team'].sort_values().unique()[i]})


# In[21]:


ids = []
for k,v in new_sample_data.groupby(by='id'):
    ids.append(k)


# In[22]:


radar_df = pd.DataFrame({'id':ids})


# In[23]:


radar_df['name'] = radar_df['id'].apply(lambda x: new_sample_data.query("id==@x")['first_name'].values[0]
                                         + ' ' + new_sample_data.query("id==@x")['second_name'].values[0])


# In[24]:


for col in new_sample_data.columns[6:]:
    if col in ['ict_index', 'selected','transfers_balance','value','ppm']:
        radar_df[col] = radar_df['id'].apply(lambda x: new_sample_data.query("id==@x")[col].mean())
    else:
        radar_df[col] = radar_df['id'].apply(lambda x: new_sample_data.query("id==@x")[col].sum())


# ### Database

# In[25]:


conn = sqlite3.connect('pl.sqlite')
cur = conn.cursor()

drop_table = '''
    DROP TABLE IF EXISTS "player_data";
'''

create_table = '''
    CREATE TABLE "player_data" (
        id INT PRIMARY KEY NOT NULL,
        player_id INT NOT NULL,
        minutes INT NOT NULL,
        goals_scored INT NOT NULL,
        assists INT NOT NULL,
        total_points INT NOT NULL
);'''

for command in [drop_table, create_table]:
    cur.execute(command)
conn.commit()
conn.close()


# In[26]:


conn = sqlite3.connect('pl.sqlite')
cur = conn.cursor()

drop_table = '''
    DROP TABLE IF EXISTS "player_name";
'''

create_table = '''
    CREATE TABLE "player_name" (
        id INT NOT NULL PRIMARY KEY UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
);'''

for command in [drop_table, create_table]:
    cur.execute(command)
conn.commit()
conn.close()


# In[27]:


conn = sqlite3.connect('pl.sqlite')
cur = conn.cursor()

insert_player = '''
        INSERT INTO player_data(id, player_id, minutes, goals_scored, assists,total_points)
        VALUES (?,?,?,?,?,?)
    '''

cur.execute(insert_player, [0, 58, 90, 0, 0, 1])
cur.execute(insert_player, [1, 19, 18, 0, 0, 1])
cur.execute(insert_player, [2, 30, 90, 0, 0, 1])
cur.execute(insert_player, [3, 70, 64, 0, 0, 2])
cur.execute(insert_player, [4, 115, 14, 0, 0, 1])

conn.commit()
conn.close()


# In[28]:


conn = sqlite3.connect('pl.sqlite')
cur = conn.cursor()

insert_player_name = '''
        INSERT INTO player_name(id, first_name, last_name)
        VALUES (?,?,?)
    '''

cur.execute(insert_player_name, [58, 'Steven', 'Cook'])
cur.execute(insert_player_name, [19, 'Lucas', 'Torriera'])
cur.execute(insert_player_name, [30, 'Anwar', 'El Ghazi'])
cur.execute(insert_player_name, [70, 'Lys', 'Mousset'])
cur.execute(insert_player_name, [115, 'Ruben', 'Loftus-Cheek'])

conn.commit()
conn.close()


# In[29]:


conn = sqlite3.connect('pl.sqlite')
cur = conn.cursor()

select_player = '''
        SELECT n.id, first_name, last_name, total_points
        FROM player_data d JOIN player_name n ON n.id=d.player_id WHERE n.id=?
    '''

cur.execute(select_player, [19])
print(cur.fetchall())

conn.commit()
conn.close()


# ### User Interaction and Visualization

# In[30]:


user_interface()

