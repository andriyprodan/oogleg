import faiss
import numpy as np

from search.constants import embedding_size, n_clusters, bi_encoder
from search.embeddings_storage import get_embeddings, embedding_cache_path


# not used
def save_index_to_file(index_name, embeddings_data, pandas_data):
    encoded_data = bi_encoder.encode(pandas_data['abstract'].values.tolist())
    encoded_data = np.asarray(encoded_data.astype('float32'))
    index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
    index.add_with_ids(encoded_data, np.array(range(0, len(pandas_data))))
    faiss.write_index(index, f'{index_name}.index')


def create_faiss_index(index_name, embeddings_data):
    ### Create the FAISS index
    quantizer = faiss.IndexFlatIP(embedding_size)
    index = faiss.IndexIVFFlat(quantizer, embedding_size, n_clusters, faiss.METRIC_INNER_PRODUCT)
    index.nprobe = 3

    print("Start creating FAISS index")
    # First, we need to normalize vectors to unit length
    corpus_embeddings = embeddings_data['embeddings'] / np.linalg.norm(embeddings_data['embeddings'], axis=1)[:, None]

    # Then we train the index to find a suitable clustering
    # todo - retrain the index every time new data is added (maybe not)
    index.train(corpus_embeddings)

    # Finally we add all embeddings to the index
    index.add(corpus_embeddings)
    # save the index
    faiss.write_index(index, f'{index_name}.index')

    print("Corpus loaded with {} sentences / embeddings".format(len(embeddings_data['db_ids'])))
    return index


def get_faiss_index(index_name, embeddings_cache_path):
    data = get_embeddings(embeddings_cache_path)
    if not data:
        return (None, None)
    try:
        return (faiss.read_index(f'{index_name}.index'), data)
    except:
        return (create_faiss_index(index_name, data), data)


# todo update faiss index every hour, use Celery cron job
# text_index, ids_data = get_faiss_index('text_index', embedding_cache_path)

# images_index, images_data = get_faiss_index('images_index', images_embeddings_cache_path)
text_index, ids_data = None, None
