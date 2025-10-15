import pandas as pd

df = pd.read_csv('all_players.csv')

sampled_returners = df[df['PlayerType'] == 'Returner'].sample(n=4, random_state=42)
sampled_transfers = df[df['PlayerType'] == 'Transfer'].sample(n=4, random_state=42)
sampled_df = pd.concat([sampled_returners, sampled_transfers], ignore_index=True)
sampled_df.to_csv("sampled_players.csv")