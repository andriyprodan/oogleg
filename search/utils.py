import pandas as pd

# not used
def convert_to_dataframe(data):
    return pd.DataFrame([{
        'abstract': data['abstracts'][i],
        'title': data['titles'][i],
        'url': data['urls'][i],
    } for i in range(len(data['abstracts']))])
