import pandas as pd 
df = pd.read_csv("transfer_portal.csv")
denver = df[df['teamMarketTo']=='Nevada']

cols = ['fullName','position','teamMarketFrom','mins','ptsScored','ast','reb']
print('\n','*'*75)
print(denver[cols])