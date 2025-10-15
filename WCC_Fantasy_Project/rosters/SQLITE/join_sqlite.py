import sqlite3
import pandas as pd

# Load CSVs
rosters = pd.read_csv("threerosters.csv")
stats = pd.read_csv("all_players.csv")

# Normalize names for joining
rosters["norm_name"] = (
    rosters["FULL NAME"].str.upper()
    .str.replace(r"[^\w\s]", "", regex=True)
    .str.strip()
)
stats["norm_name"] = (
    stats["Player"].str.upper()
    .str.replace(r"[^\w\s]", "", regex=True)
    .str.strip()
)

# Write to SQLite
conn = sqlite3.connect("fantasy.db")
rosters.to_sql("rosters", conn, if_exists="replace", index=False)
stats.to_sql("stats", conn, if_exists="replace", index=False)

test = pd.read_sql("""
SELECT r.norm_name, s.norm_name
FROM rosters r
LEFT JOIN stats s
    ON r.norm_name = s.norm_name
LIMIT 50;
""", conn)

print(test.head(20))

#so theres a lot more columns that we could be using but right now we're 
# only using name , pos, ht, year, school, and needs projection 


# Create the view (no DataFrame yet)
create_view = """
CREATE VIEW IF NOT EXISTS draft_board AS
SELECT 
    r."FULL NAME",
    r."POS.",
    r."HT.",
    r."Academic Year",
    r."Previous School",
    CASE 
        WHEN s.norm_name IS NULL THEN 'NEEDS PROJECTION'
        ELSE 'HAS PROJECTION'
    END AS Status
FROM rosters r
LEFT JOIN stats s
    ON r.norm_name = s.norm_name;
"""
conn.execute(create_view)
print(pd.read_sql("SELECT name, type FROM sqlite_master WHERE type='table';", conn))

# Now query the view into a DataFrame
draft_board = pd.read_sql("SELECT * FROM draft_board", conn)
print(draft_board["Status"].value_counts())
#print(draft_board.head(33))
draft_board.to_csv("draft_board_test.csv")

