import streamlit as st
import pandas as pd
from unidecode import unidecode

st.set_page_config(page_title="Player Game Logs", page_icon="📅")

st.title("📅 Player Game Logs")

# --- Load Data ---
@st.cache_data
def load_data():
    fantasy_stats = pd.read_csv("data/fantasy/fantasy_stats_latest.csv")
    gamelog = pd.read_csv("Gamelog/gamelog.csv")
    return fantasy_stats, gamelog

fantasy_stats, gamelog = load_data()

# --- Clean and prep ---
def make_clean_name(name):
    return unidecode(name.strip().lower()) if isinstance(name, str) else ""

# --- 1️⃣ Master Game Log Viewer ---
st.subheader("📜 All Game Logs")

# Convert Date column
if "Date" in gamelog.columns:
    gamelog["Date"] = pd.to_datetime(gamelog["Date"], errors="coerce").dt.date


# Date range filter
min_date = gamelog["Date"].min()
max_date = gamelog["Date"].max()
start_date, end_date = st.date_input(
    "Filter by date range:",
    value=(max_date - pd.Timedelta(days=1), max_date),
    min_value=min_date,
    max_value=max_date
)
filtered_gamelog = gamelog[
    (gamelog["Date"].apply(lambda x: x.date() if isinstance(x, pd.Timestamp) else x) >= start_date) &
    (gamelog["Date"].apply(lambda x: x.date() if isinstance(x, pd.Timestamp) else x) <= end_date)
]


st.dataframe(
    gamelog.sort_values("Date", ascending=False)[
        ["Date", "Name", "Team", "Opponent", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "FantasyPts"]
    ],
    use_container_width=True,
    height=400
)

st.markdown("---")

# --- 2️⃣ Individual Player Selector ---
st.subheader("🎯 Player Search")

players = fantasy_stats["Full Name"].dropna().unique().tolist()
player = st.selectbox("Select a player:", sorted(players))

clean_player = make_clean_name(player)

player_logs = gamelog[gamelog["Name"].apply(make_clean_name) == clean_player]
# Display player image if available
if not player_logs.empty and 'ImageURL' in fantasy_stats.columns:
    player_image_url = fantasy_stats[fantasy_stats['Full Name'] == player]['ImageURL'].iloc[0]
    if pd.notna(player_image_url):
        st.image(player_image_url, width=120)


if not player_logs.empty:
    st.subheader(f"📈 {player} — Game Log")
    st.dataframe(
        player_logs[
            ["Date", "Team", "Opponent", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "FantasyPts"]
        ].sort_values("Date", ascending=False),
        use_container_width=True
    )

    st.line_chart(
        player_logs.sort_values("Date"),
        x="Date", y="FantasyPts", use_container_width=True
    )
else:
    st.info("No game logs found for this player yet.")
