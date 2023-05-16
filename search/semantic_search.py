import time

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder

from search.constants import model_name, embedding_size, n_clusters
from search.faiss_index import text_data
from search.utils import convert_to_dataframe


def fetch_article_info(dataframe_idx):
    pandas_data = convert_to_dataframe(text_data)
    info = pandas_data.iloc[dataframe_idx]
    meta_dict = {}
    meta_dict['url'] = info['url']
    meta_dict['abstract'] = info['abstract']
    meta_dict['title'] = info['title']
    return meta_dict


def search(query, top_k, index, model):
    t = time.time()
    query_vector = model.encode([query])
    top_k = index.search(query_vector, top_k)
    print('>>>> Results in Total Time: {}'.format(time.time() - t))
    top_k_ids = top_k[1].tolist()[0]
    top_k_ids = list(np.unique(top_k_ids))
    results = [fetch_article_info(idx) for idx in top_k_ids]
    return results
