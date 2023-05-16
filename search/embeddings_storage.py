import os
import pickle

import faiss
import numpy as np
import pandas as pd
from django.conf import settings
from django.db.models import QuerySet

from search.constants import model_name, max_corpus_size, embedding_size, n_clusters, bi_encoder

embedding_cache_path = settings.BASE_DIR / 'abstract-embeddings-{}-size-{}.pkl'.format(model_name, max_corpus_size)
images_embeddings_cache_path = settings.BASE_DIR / 'images-abstract-embeddings-{}-size-{}.pkl'.format(model_name,
                                                                                                      max_corpus_size)


def write_embeddings(web_resources):
    pickle_data = {}
    # todo - store the embeddings in a database instead of a file
    # OR todo - don't overwrite the file if it already exists, instead append to it
    print("Encode the corpus. This might take a while")
    abstracts = [wr.abstract for wr in web_resources]
    corpus_embeddings = bi_encoder.encode(abstracts, show_progress_bar=True,
                                          convert_to_numpy=True)
    print("Store file on disc")
    pickle_data['db_ids'] = [wr.id for wr in web_resources]
    pickle_data['embeddings'] = corpus_embeddings
    with open(embedding_cache_path, "wb") as fOut:
        pickle.dump(pickle_data, fOut)


def get_embeddings(cache_path):
    if not os.path.exists(cache_path):
        return None

    print("Load pre-computed embeddings from disc")
    with open(cache_path, "rb") as fIn:
        cache_data = pickle.load(fIn)
        data = {
            'db_ids': cache_data['db_ids'],
            'embeddings': cache_data['embeddings'],
        }
    return data


