import json
import pandas as pd


def read_json(path):
    with open(path) as f:
        data = json.load(f)
    return data


json_data = read_json('./startups.json')
df = pd.DataFrame(json_data)

df_flattened = pd.json_normalize(df['data'])
df_combined = pd.concat([df, df_flattened], axis=1)
df_combined = df_combined.drop('data', axis=1)
# display(HTML(df_combined.to_html()))
df_combined.to_csv('./data.csv', index=False)
print("The file has been saved as ./data.csv")
