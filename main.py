import pandas as pd
import numpy as np
from itertools import combinations
from random import shuffle, sample
import gdown

url = 'insert download url code here for google sheet file'
output = 'Fotbal.xlsx'
gdown.download(url, output, quiet=False)
print()

# Load data into a DataFrame
data = pd.read_excel('Fotbal.xlsx', sheet_name='Jucatori')

# Calculating Overall based on stats
ponderi = pd.read_excel('Fotbal.xlsx', sheet_name='Ponderi', index_col=0)


def calcul_overall(jucator, ponderi):
    # Calculul sumei ponderilor pentru poziția jucătorului
    suma_ponderi = ponderi.loc[jucator['Pozitie']].sum()

    # Verifică valoarea din coloana 'INFORM' și ajustează overall-ul
    if jucator['INFORM'] != 0:
        bonus_inform = jucator['INFORM']
    else:
        bonus_inform = 0

    overall = round(
        ((jucator['PAC'] * ponderi.loc[jucator['Pozitie'], 'PAC'] +
          jucator['SHO'] * ponderi.loc[jucator['Pozitie'], 'SHO'] +
          jucator['PAS'] * ponderi.loc[jucator['Pozitie'], 'PAS'] +
          jucator['DRI'] * ponderi.loc[jucator['Pozitie'], 'DRI'] +
          jucator['DEF'] * ponderi.loc[jucator['Pozitie'], 'DEF'] +
          jucator['PHY'] * ponderi.loc[jucator['Pozitie'], 'PHY']) / suma_ponderi) + bonus_inform,
        0)
    return overall


data['Overall'] = data.apply(calcul_overall, axis=1, ponderi=ponderi)


# Selecting players with 'Prezenta' marked as 1
available_players = data[data['Prezenta'] == 1]


# Sorting by 'Overall' to balance teams
sorted_players = available_players.sort_values(by='Overall', ascending=False)


# Function to check the average overall of the teams
def check_balance(teams):
    averages = [np.mean([player['Overall'] for player in team]) for team in teams]
    return max(averages) - min(averages) <= 0.25


# Function to generate balanced teams
def generate_balanced_teams(sorted_players, n_teams=3, team_size=5, max_attempts=100000):
    all_players = sorted_players.to_dict('records')
    best_combination = None
    min_difference = float('inf')

    # Attempt to generate balanced teams a maximum number of times
    for _ in range(max_attempts):
        players_list = sample(all_players, n_teams * team_size)  # Randomly sample without replacement
        teams = [players_list[i:i + team_size] for i in range(0, len(players_list), team_size)]
        if check_balance(teams):
            # Calculate the total overall difference between teams
            averages = [np.mean([player['Overall'] for player in team]) for team in teams]
            difference = max(averages) - min(averages)
            if difference < min_difference:
                min_difference = difference
                best_combination = teams
            break  # Break if a balanced combination is found

    return best_combination


# Generate the teams with the available players
teams = generate_balanced_teams(sorted_players)
team_list = []  # List to store team data
screenshot_list = [] # List to share on Whatsapp

# If teams were generated successfully, prepare them for Excel output
if teams:
    for i, team in enumerate(teams, 1):
        team_overall = np.mean([player['Overall'] for player in team])  # Calculate team's average overall
        team_list.append(["Team {}".format(i), "Overall", "{:.2f}".format(team_overall)])  # Append team name and overall to list
        for player in team:
            team_list.append([' ', player['Nume'], player['Overall']])  # Append player data
        team_list.append([' ', ' ', ' '])  # Append an empty row for spacing between teams

    for i, team in enumerate(teams, 1):
      screenshot_list.append(["Team {}".format(i), " "])  # Append team name and overall to list
      for player in team:
          screenshot_list.append([' ', player['Nume']])  # Append player data
      screenshot_list.append([' ', ' '])  # Append an empty row for spacing between teams
else:
    print("No balanced teams could be found.")

# Convert the team list to a DataFrame
teams_df = pd.DataFrame(team_list, columns=['Team', 'Name', 'Overall'])
screenshot_df = pd.DataFrame(screenshot_list, columns=['Team', 'Name'])
print(teams_df)

for i in range(10):
  print()

print(screenshot_df)

# Write the teams DataFrame to the 'Echipe' sheet in the Excel file
with pd.ExcelWriter('Fotbal.xlsx', mode='a', if_sheet_exists='replace') as writer:  # Open the Excel file
    teams_df.to_excel(writer, sheet_name='Echipe', index=False)  # Write the DataFrame to the 'Echipe' sheet

# The 'Fotbal.xlsx' Excel file now contains the teams and their overalls in the 'Echipe' sheet.
