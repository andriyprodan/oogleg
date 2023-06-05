import pandas as pd

from search.constants import bi_encoder


# not used
def convert_to_dataframe(data):
    return pd.DataFrame([{
        'abstract': data['abstracts'][i],
        'title': data['titles'][i],
        'url': data['urls'][i],
    } for i in range(len(data['abstracts']))])


def encode_string(text):
    return bi_encoder.encode(text, convert_to_tensor=True)


