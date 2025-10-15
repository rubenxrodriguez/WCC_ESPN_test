import streamlit as st
import pandas as pd
import glob
import random


# add barriers in between user teams 
st.set_page_config(page_title="WBB Draft Board", layout="wide")
st.title("🏀 WBB Fantasy Draft Board")

# --- Load all roster CSVs ---
files = glob.glob("rosters/*_roster.csv")
teams = {f.split("/")[-1].replace("_roster.csv", ""): pd.read_csv(f) for f in files}
teams_list = ['gonzaga','lmu','osu','pepperdine','santa clara','santa clara','seattle','smc','wsu']

# --- Section 1: Select Teams ---
team_names = list(teams.keys())
selected_teams = st.multiselect(
    "Select teams for the trade board", 
    team_names, 
    default=team_names[:3], 
    max_selections=3
)

if selected_teams:
    # Combine all selected team rosters
    #all_players = pd.concat([teams[team] for team in selected_teams], ignore_index=True)
    all_players = pd.read_csv("web_app/wcc_concat_copy.csv")
    # --- Section 2: Top Draft Prospects Board ---
    st.markdown("## 🌟 Top Draft Prospects")
    
    # Assign random ADP for demonstration
    #all_players["ADP"] = [random.randint(1, len(all_players)) for _ in range(len(all_players))]
    #all_players.to_csv("all_players.csv")
    # Show top 5 by ADP
    top5 = all_players.nsmallest(5, "ADP")
    
    top_cols = st.columns(5)
    for idx, (_, row) in enumerate(top5.iterrows()):
        with top_cols[idx]:
            st.image(row["ImageURL"], width=100)
            st.markdown(f"**{row['Full Name']}**")
            st.markdown(f"ADP: {row['ADP']}")
            st.markdown(f"{row['Pos.']} | {row['Ht.']} | {row['Year']}")
    
    st.markdown("---")
    
    # --- Section 3: User Teams Draft Board ---
    user_teams = {"UserTeam1": [], "UserTeam2": [], "UserTeam3": []}

    
    st.markdown("---")
    st.subheader("Drafted Players by User Team")
    
    # Draft players to user teams
    for ut in user_teams.keys():
        user_teams[ut] = st.multiselect(
            f"Draft players to {ut}", 
            all_players["Full Name"].tolist(),
            default=[]
        )
    
    # Display drafted players for each user team
    for ut, players in user_teams.items():
        st.markdown(f"### {ut}")
        for player in players:
            player_row = all_players[all_players["Full Name"] == player].iloc[0]
            st.image(player_row["ImageURL"], width=80)
            st.markdown(
                f"**{player_row['Full Name']}** | {player_row['Pos.']} | {player_row['Ht.']} | {player_row['Year']}"
            )
