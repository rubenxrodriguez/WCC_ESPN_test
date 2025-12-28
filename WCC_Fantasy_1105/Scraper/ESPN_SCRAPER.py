from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import os
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

def safe_get_text(driver, xpath, label="value", allow_manual=True):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except (NoSuchElementException, TimeoutException) as e:
        print(f"\n⚠️ Failed to scrape {label}")
        print(f"XPath: {xpath}")
        print(f"Error: {type(e).__name__}")

        if allow_manual:
            manual = input(f"➡️ Enter {label} manually (or press Enter to skip): ").strip()
            return manual if manual else None
        return None


def get_indices(rows_text):
    starters_counter = 0
    team_counter = 0
    firstplayerindex1=firstplayerindex2=lastplayerindex1=lastplayerindex2 = 0
    while(True):
        if starters_counter<1 and team_counter<1 :
            #then the next row and up to "TEAM" will be Team1 Names
            firstplayerindex1 = rows_text.index("STARTERS")+1
            lastplayerindex1 = rows_text.index("TEAM")-1
            starters_counter+=1
            team_counter+=1
        else:
            look = rows_text[lastplayerindex1+2:]
            firstplayerindex2 = look.index("STARTERS")+1+lastplayerindex1+2
            #print(look.index("TEAM"))
            lastplayerindex2 = look.index('TEAM')-1+lastplayerindex1+2
            break
    firststatsindex1 = lastplayerindex1 + 3
    laststatsindex1 = firststatsindex1 + (lastplayerindex1-firstplayerindex1+1)

    firststatsindex2 = lastplayerindex2 + 3
    laststatsindex2 = firststatsindex2 + (lastplayerindex2-firstplayerindex2+1) #these are the indices but if we want to graph the rows we use range(firststatsindex2,laststatsindex2+1)
    return firstplayerindex1,lastplayerindex1,firststatsindex1,laststatsindex1,firstplayerindex2,lastplayerindex2,firststatsindex2,laststatsindex2
def process_team_data(player_rows, name_start, name_end, stats_start, stats_end):
    # Extract player name + jersey lines
    raw_names = [player.text.replace("\n", " ") for player in player_rows[name_start:name_end]]
    raw_names.pop(5)  # Remove element at index 5 (Totals row, usually)

    # Split into Name and Jersey
    names = []
    jerseys = []
    for entry in raw_names:
        parts = entry.split()
        if parts[-1].split('#')[-1].isdigit():  
            jerseys.append(parts[-1])   # last token is jersey number
            names.append(" ".join(parts[:-1]))  # everything before jersey
        else:
            jerseys.append("")  # in case something’s off
            names.append(entry)

    # Extract stats rows
    stats = [player.text.replace("\n", " ") for player in player_rows[stats_start+1:stats_end]]
  
    
    # Extract column names
    colnames = stats[5].split(' ')
    colnames.insert(0, "Name")
    colnames.insert(1,"Jersey #")
    stats.pop(5)

    # Create a list of player stats
    player_stats = []
    for i in range(len(names)):
        temp_stats = stats[i].split(" ")
        temp_stats.insert(0, names[i])
        temp_stats.insert(1,jerseys[i])
        player_stats.append(temp_stats)

    # Create a DataFrame
    df = pd.DataFrame(player_stats, columns=colnames)


    
    return df

def calculate_fantasy_points(row):
    #print(row["Name"])
    # Define rules for calculating fantasy points for each stat
    points_dict = {
        'FGM': 2,
        'FGA': -1,
        'FTM': 1,
        'FTA': -1,
        '3PM': 2,
        '3PA': -1,
        'OREB': 1,
        'DREB': 1,
        'AST': 3,
        'STL': 4,
        'BLK': 3,
        'TO': -2,
        'PTS': 1,
        'didWin': 1  # we skip this for season totals
    }

    fantasy_points = 0
    for stat, weight in points_dict.items():
        if stat in row and pd.notna(row[stat]):
            try:
                fantasy_points += weight * int(row[stat])
            except ValueError:
                pass
    return fantasy_points


# --- KEEP YOUR EXISTING UTILS ---
# from your_code import get_indices, process_team_data, calculate_fantasy_points
def expand_shooting_stats(df):
    # ESPN gives FG, 3PT, FT in "x-y" format
    if "FG" in df.columns:
        df[["FGM", "FGA"]] = df["FG"].str.split("-", expand=True).astype(int)
        df.drop(columns=["FG"], inplace=True)

    if "3PT" in df.columns:
        df[["3PM", "3PA"]] = df["3PT"].str.split("-", expand=True).astype(int)
        df.drop(columns=["3PT"], inplace=True)

    if "FT" in df.columns:
        df[["FTM", "FTA"]] = df["FT"].str.split("-", expand=True).astype(int)
        df.drop(columns=["FT"], inplace=True)

    return df
def scrape_dailyboxscores(websites, csv_file_name, folder_path):
    """
    Scrape daily box scores from ESPN scoreboard pages and save the data to CSV files.

    Parameters:
    - websites (list): List of URLs for daily box score pages.
    - csv_file_name (str): The name to use when saving the CSV file.
    - folder_path (str): The folder path where the CSV file will be saved.

    Returns:
    - pd.DataFrame: A DataFrame containing the scraped data.
    """
    formatted_date = 'N/A'
    dataframes = []

    for website in websites:
        i = 1
        while True:
            driver = webdriver.Chrome()
            driver.get(website)
                    #/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/div[1]/div/div/section/div/section/div[2]/a[2]
                    #/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/div[1]/div/div/section/div/section[1]/div[2]/a[2]
                    # change section 5 to section[{i}]
            xpatha = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div[1]/div[1]/div/div/section/div/section[{i}]/div[2]/a[2]'
                
            xpathb = '/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/div[1]/div/div/section/header/div[1]'
                    
            try:
                # Find the box score button
                try:
                    xpatha_ = driver.find_element(By.XPATH, xpatha)
                except (NoSuchElementException, ValueError):
                    print("No more box scores found.\n")
                    driver.quit()
                    break

                # Get the Date from the scoreboard page
                try:
                    xpathb_ = driver.find_element(By.XPATH, xpathb).text
                    time.sleep(1.8)
                    date_object = datetime.strptime(xpathb_, '%A, %B %d, %Y')
                    formatted_date = date_object.strftime('%m/%d/%y')
                except (NoSuchElementException, ValueError):
                    print("Date not found with outer div class.\n")

                # Click box score
                xpatha_.click()
                time.sleep(2.5)

                # Extract player rows
                player_rows = driver.find_elements(By.CLASS_NAME, "Table__TR.Table__TR--sm.Table__even")
                time.sleep(2.9)
                rows_text = [player.text for player in player_rows]
                print(rows_text[:3])

                # Split into team 1 and team 2
                namestart1, nameend1, statstart1, statend1, namestart2, nameend2, statstart2, statend2 = get_indices(rows_text)

                team1_df = process_team_data(player_rows, namestart1, nameend1 + 1, statstart1, statend1 + 1)
                team1_df = expand_shooting_stats(team1_df)
                team2_df = process_team_data(player_rows, namestart2, nameend2 + 1, statstart2, statend2 + 1)
                team2_df = expand_shooting_stats(team2_df)
                #team1_df['Name'] = team1_df['Name'].str.rstrip('#')
                #team2_df['Name'] = team2_df['Name'].str.rstrip('#') 
                
                fullteamname1 = safe_get_text(
                    driver,
                    '/html/body/div[1]/div/div/div/div/main/div[2]/div/div[2]/div/div[2]/div[2]/div/div/section[1]/div/div/div/div[1]/div/div[1]/div[1]',
                    label="Full Team Name (Away)"
                )

                fullteamname2 = safe_get_text(
                    driver,
                    '/html/body/div[1]/div/div/div/div/main/div[2]/div/div[2]/div/div[2]/div[2]/div/div/section[1]/div/div/div/div[2]/div/div[1]/div[1]',
                    label="Full Team Name (Home)"
            )
                # Insert columns
                for df, team, opp in [(team1_df, fullteamname1, fullteamname2),
                                      (team2_df, fullteamname2, fullteamname1)]:
                    df.insert(2, "Team", team)
                    df.insert(3, "Date", formatted_date)
                    df.insert(len(df.columns) - 1, "Opponent", opp)
                
                score1 = team1_df["PTS"].astype(int).sum()
                score2 = team2_df["PTS"].astype(int).sum()

                if score1 > score2:
                    team1_win, team2_win = 1, 0
                else:
                    team1_win, team2_win = 0, 1

                team1_df["didWin"] = team1_win
                team2_df["didWin"] = team2_win
                
                
                # Apply Fantasy Points
                team1_df["FantasyPts"] = team1_df.apply(calculate_fantasy_points, axis=1)
                team2_df["FantasyPts"] = team2_df.apply(calculate_fantasy_points, axis=1)
                print(f"✅ Scraped: {fullteamname1} vs {fullteamname2} on {formatted_date}")
                column_order = ['Name', 'Jersey #', 'Team','Opponent','didWin', 'Date', 'MIN', 'OREB', 'DREB', 'REB', 'AST',
                                'STL', 'BLK', 'TO', 'PF', 'FGM', 'FGA', '3PM', '3PA', 'FTM','FTA',
                                'PTS', 'FantasyPts']
                team1_df = team1_df[column_order]
                team2_df = team2_df[column_order]
                dataframes.append(team1_df)
                dataframes.append(team2_df)
                
            except Exception as e:
                print(f"An error occurred: {str(e)}")

            driver.quit()
            i += 1

        print(f"-----\nEnd of Day {formatted_date}\n-----")

    # Write the concatenated data to a CSV file
    concatenated_df = pd.concat(dataframes, ignore_index=True)
    os.makedirs(folder_path, exist_ok=True)
    csv_file_path = os.path.join(folder_path, csv_file_name)
    
        # --- Append or write logic ---
    if os.path.exists(csv_file_path):
        # Append without headers
        concatenated_df.to_csv(csv_file_path, index=False, mode='a', header=False)
    else:
        # Write new file with headers
        concatenated_df.to_csv(csv_file_path, index=False, mode='w', header=True)
    concatenated_df = concatenated_df.drop_duplicates(subset=['Name','Team','Date'])
    return concatenated_df

website = [
    f"https://www.espn.com/womens-college-basketball/scoreboard/_/date/202511{d:02d}/group/29"
    for d in range(11, 15)
]

csv_file_name = f'gamelog.csv'
folder_path = 'Gamelog'
df_result = scrape_dailyboxscores(websites=website,csv_file_name=csv_file_name,folder_path=folder_path)
time.sleep(3)