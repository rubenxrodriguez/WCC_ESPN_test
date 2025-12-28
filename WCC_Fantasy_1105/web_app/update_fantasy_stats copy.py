import pandas as pd
import unidecode
from datetime import date,timedelta
import os

# --- 0️⃣ Paths ---
DRAFT_PATH = "data/Draft Board Updated.csv"
RESULTS_PATH = "data/draft_results.csv"
GAMELOG_PATH = "Gamelog/gamelog.csv"
OUTPUT_DIR = "data/fantasy/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1️⃣ Load core sources ---
draft = pd.read_csv(DRAFT_PATH)
draft_results = pd.read_csv(RESULTS_PATH)
gamelogs = pd.read_csv(GAMELOG_PATH)

# --- 2️⃣ Map player → userteam ---
userteam_map = dict(zip(draft_results['Player'], draft_results['Team']))

# Keep relevant columns & rename
draft = draft[['#', 'Full Name', 'FullTeamName', 'Pos.', 'Ht.', 'Year',
               'Hometown', 'Previous School', 'clean_name', 'Player',
               'Team_prev', 'conf', 'ImageURL', 'Team', 'NewTeam', 'NewConf']]

draft.columns = ['#', 'Full Name', 'FullTeamName', 'Pos.', 'Ht.', 'Year',
                 'Hometown', 'Previous School', 'clean_name', 'Player',
                 'Team_prev', 'Previous Conf', 'ImageURL', 'Team', 'NewTeam', 'NewConf']

# Assign userteam or mark as FreeAgent
draft['userteam'] = draft['Full Name'].map(userteam_map).fillna('FreeAgent')

# --- 3️⃣ Clean gamelog player names ---
def make_clean_name(name):
    if pd.isna(name):
        return ""
    return unidecode.unidecode(name.strip().lower())

gamelogs['clean_name'] = gamelogs['Name'].apply(make_clean_name)

# --- 4️⃣ Aggregate gamelogs ---
agg = gamelogs.groupby('clean_name').agg({
    'FantasyPts': ['sum', 'mean', 'count'],
    'MIN': ['sum', 'mean'],
    'OREB': ['sum', 'mean'],
    'DREB': ['sum', 'mean'],
    'REB': ['sum', 'mean'],
    'AST': ['sum', 'mean'],
    'STL': ['sum', 'mean'],
    'BLK': ['sum', 'mean'],
    'TO': ['sum', 'mean'],
    'FGM': ['sum', 'mean'],
    'FGA': ['sum', 'mean'],
    '3PM': ['sum', 'mean'],
    '3PA': ['sum', 'mean'],
    'FTM': ['sum', 'mean'],
    'FTA': ['sum', 'mean'],
    'PTS': ['sum', 'mean']
}).reset_index()

# Flatten column names
agg.columns = ['_'.join(col).rstrip('_') for col in agg.columns.values]

# --- 5️⃣ Merge aggregated data into draft board ---
fantasy_stats = draft.merge(agg, how='left', on='clean_name').fillna(0)

# --- 6️⃣ Rankings ---
fantasy_stats['rank_pos'] = fantasy_stats.groupby('Pos.')['FantasyPts_sum'].rank(ascending=False)
fantasy_stats['rank_global'] = fantasy_stats['FantasyPts_sum'].rank(ascending=False)
fantasy_stats['GP'] = fantasy_stats['FantasyPts_count']
# --- 7️⃣ Reorder columns ---
fantasy_stats = fantasy_stats[[
    '#', 'Full Name', 'FullTeamName', 'Pos.', 'Ht.', 'Year', 'Hometown',
    'userteam', 'FantasyPts_sum', 'FantasyPts_mean', 'rank_pos', 'rank_global',
    'GP', 'MIN_mean', 'PTS_mean', 'REB_mean', 'AST_mean', 'STL_mean',
    'BLK_mean', '3PM_mean', '3PA_mean', 'FTM_mean', 'TO_mean', 'FGM_mean', 'FGA_mean',
    'OREB_sum', 'OREB_mean', 'DREB_sum', 'DREB_mean', 'MIN_sum', 'PTS_sum', 'REB_sum',
    'AST_sum', 'STL_sum', 'BLK_sum', 'TO_sum', 'FGM_sum', 'FGA_sum', '3PM_sum', '3PA_sum',
    'FTM_sum', 'FTA_sum', 'FTA_mean', 'Previous School', 'clean_name', 'Player',
    'Team_prev', 'Previous Conf', 'Team', 'NewTeam', 'NewConf', 'ImageURL'
]]

# --- 8️⃣ Round numbers ---
fantasy_stats = fantasy_stats.round(2)

# --- 9️⃣ Save outputs ---

today = date.today().strftime("%Y-%m-%d")
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
output_file = os.path.join(OUTPUT_DIR, f"fantasy_stats_{today}.csv")

fantasy_stats.to_csv(output_file, index=False)
fantasy_stats.to_csv(os.path.join(OUTPUT_DIR, "fantasy_stats_latest.csv"), index=False)

print(f"✅ Fantasy stats updated and saved to:\n{output_file}")
print(fantasy_stats[['Full Name', 'userteam', 'FantasyPts_sum', 'rank_global']].head(10))
