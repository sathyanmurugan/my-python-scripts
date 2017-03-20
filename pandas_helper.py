import pandas as pd


df = pd.read_csv(path_to_csv,encoding='utf8')

#read as datetime
df['Date']  = pd.to_datetime(df['Date'],format='%Y-%m-%d %H:%M:%S')

#convert to specific date format
df['survey_date'] = df['Date Submitted'].apply(lambda row: row.strftime('%Y-%m'))

#extract certain columns as Dataframe
df = df[['survey_date',poll_name]]

#case operations when looping
df[poll_name] = df[poll_name].apply(lambda row: 
	'detractors' if row < 7 else
	'passive' if row >= 7 and row < 9 else
	'promoters'
	)

#Groupby, sum, convert to DF
df = pd.DataFrame(df.groupby('survey_date').sum())

#Mark column as index
df['survey_date'] = df.index

#Change column type
df['nps_score'] = df['nps_score'].astype(int)

#Melt
df = pd.melt(df,id_vars=['survey_date'],var_name='type')

df = df.rename(columns={'Id':'OwnerId'})

#NaN to None
df = df.where((pd.notnull(df)), None)

#Get all csvs in output folder
csv_files = [os.path.join(output_folder,file) for file in os.listdir(output_folder) if file.endswith(".csv")]

dfs = []
for file in csv_files:
	df = pd.read_csv(file,encoding='utf8')
	df = df[df['Transaction Date (Monthly)'] !='Grand Total']
	dfs.append(df)

df_all = pd.concat(dfs,ignore_index=True)
df_all.to_csv('test.csv',index=False)