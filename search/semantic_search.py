import time

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder

from articles.models import WebResource
from search.constants import model_name, embedding_size, n_clusters
from search.faiss_index import ids_data
from search.utils import convert_to_dataframe


def fetch_web_resource_info(dataframe_idx):

    db_id = ids_data['db_ids'][dataframe_idx]

    return WebResource.objects.get(id=db_id)


def search(query, top_k, index, model):
    t = time.time()
    query_vector = model.encode([query])
    top_k = index.search(query_vector, top_k)
    print('>>>> Results in Total Time: {}'.format(time.time() - t))
    top_k_ids = top_k[1].tolist()[0]
    top_k_ids = list(np.unique(top_k_ids))
    results = [fetch_web_resource_info(idx) for idx in top_k_ids]
    return results
