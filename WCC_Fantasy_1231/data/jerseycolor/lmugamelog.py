import pandas as pd 
df = pd.read_csv("Gamelog/gamelog.csv")
LMU = "Loyola Marymount Lions"
df = df[(df['Team'] == LMU) | (df['Opponent'] == LMU)]
df.to_csv('data/jerseycolor/lmugamelog0105.csv',index=False)