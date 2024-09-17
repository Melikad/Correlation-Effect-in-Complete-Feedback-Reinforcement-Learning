import pandas as pd

# Create an empty list to hold the DataFrames
df = pd.DataFrame()

# Loop through the range from 1 to 10 to read each CSV
for i in range(10):
    file_name = 'learning_data_' + str(i+1) + '.csv'
    df = pd.concat([df, pd.read_csv(file_name)])

a1_n_records = pd.DataFrame()
a2_n_records = pd.DataFrame()
a1_z_records = pd.DataFrame()
a2_z_records = pd.DataFrame()
a1_p_records = pd.DataFrame()
a2_p_records = pd.DataFrame()

a1_n_records = pd.concat([a1_n_records, df[df['Image Left'] == 'images/tibetian/a1_N.png']])
a2_n_records = pd.concat([a2_n_records, df[df['Image Left'] == 'images/tibetian/a2_N.png']])
a1_z_records = pd.concat([a1_z_records, df[df['Image Left'] == 'images/tibetian/a1_Z.png']])
a2_z_records = pd.concat([a2_z_records, df[df['Image Left'] == 'images/tibetian/a2_Z.png']])
a1_p_records = pd.concat([a1_p_records, df[df['Image Left'] == 'images/tibetian/a1_P.png']])
a2_p_records = pd.concat([a2_p_records, df[df['Image Left'] == 'images/tibetian/a2_P.png']])

    
print('Decision Time')
print(a1_n_records['Decision Time'].mean())
print(a2_n_records['Decision Time'].mean())
print(a1_z_records['Decision Time'].mean())
print(a2_z_records['Decision Time'].mean())
print(a1_p_records['Decision Time'].mean())
print(a2_p_records['Decision Time'].mean())

print('Feedback Time')
print(a1_n_records['Feedback Time'].mean())
print(a2_n_records['Feedback Time'].mean())
print(a1_z_records['Feedback Time'].mean())
print(a2_z_records['Feedback Time'].mean())
print(a1_p_records['Feedback Time'].mean())
print(a2_p_records['Feedback Time'].mean())

print('Gained Value')
print(a1_n_records['Gained Value'].mean())
print(a2_n_records['Gained Value'].mean())
print(a1_z_records['Gained Value'].mean())
print(a2_z_records['Gained Value'].mean())
print(a1_p_records['Gained Value'].mean())
print(a2_p_records['Gained Value'].mean())

def accuracy(df):
    return len(df[df['Gained Value'] == df[['Value Left', 'Value Right']].max(axis=1)])/350


print('Accuracy')
print(accuracy(a1_n_records))
print(accuracy(a2_n_records))
print(accuracy(a1_z_records))
print(accuracy(a2_z_records))
print(accuracy(a1_p_records))
print(accuracy(a2_p_records))
