import pandas as pd
from unidecode import unidecode
import numpy as np

# Load existing wcc_concat
df = pd.read_csv("rosters/teams/wcc_concat.csv")

# Map from canonical Team key → Full display name
TEAM_TO_FULL = {
    "santa clara": "Santa Clara Broncos",
    "lmu": "Loyola Marymount Lions",
    "osu": "Oregon State Beavers",
    "gonzaga": "Gonzaga Bulldogs",
    "usf": "San Francisco Dons",
    "wsu": "Washington State Cougars",
    "pacific": "Pacific Tigers",
    "pepperdine": "Pepperdine Waves",
    "smc": "Saint Mary's Gaels",
    "seattle": "Seattle U Redhawks",
    "portland": "Portland Pilots",
    "san diego": "San Diego Toreros",
}

def clean_player_name(name: str) -> str:
    if pd.isna(name):
        return ""
    name = unidecode(str(name))
    name = name.lower().strip()
    name = " ".join(name.split())
    return name

# Add new columns
df["FullTeamName"] = df["Team"].map(TEAM_TO_FULL)
df["clean_name"] = df["Full Name"].apply(clean_player_name)


OUTPUT_COLUMNS = [
    "#",
    "Full Name",
    "FullTeamName",
    "Team",
    "Pos.",
    "Ht.",
    "Year",
    "Hometown",
    "Previous School",
    "ImageURL",
    "clean_name",
]
df = df[OUTPUT_COLUMNS]
df["ADP"] = np.random.randint(1, len(df) + 1, size=len(df))

# Save back
df.to_csv("rosters/teams/wcc_concat_updated.csv", index=False)
print("File Saved")