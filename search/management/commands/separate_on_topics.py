import spacy
from autocorrect import Speller
from django.conf import settings
from django.core.management import BaseCommand
from rdflib import URIRef, Literal, RDF
from top2vec import Top2Vec
from torchvision.datasets import voc

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph
from rdf_ontologies.constants import oogleg_voc

nlp = spacy.load("uk_core_news_trf")


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('reduced_topics.txt', 'r', encoding='utf-8') as f:
            reduced_topics = set(f.read().split('\n') )
        documents = []
        document_ids = []
        for wr in WebResource.objects.all():
            document_ids.append(wr.id)
            abstract = wr.content_without_html
            # leave only letters, numbers, spaces and dots for abstracts
            # abstract = ''.join([c for c in abstract if c.isalpha() or c.isdigit() or c.isspace() or c == '.'])
            # abstract = ' '.join(abstract.split(' ')[:128])
            documents.append(abstract)
        try:
            model = Top2Vec.load("top2vec_model.bin")
        except:
            umap_args = {
                'n_neighbors': 10,
                'n_components': 5,
                'metric': 'cosine',
                'random_state': 42
            }

            hdbscan_args = {
                'min_cluster_size': 10,
                'min_samples': 5,
                'metric': 'euclidean',
                'cluster_selection_method': 'eom'
            }
            model = Top2Vec(documents=documents, document_ids=document_ids, speed='deep-learn', workers=8, min_count=0,
                            embedding_model='distiluse-base-multilingual-cased',
                            # embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
                            umap_args=umap_args, hdbscan_args=hdbscan_args)
            model.min_topic_size = 200
            model.save("top2vec_model.bin")

        spell = Speller('uk')

        def get_corrected_topics(topic_words):
            corrected = spell(' '.join(topic_words))
            corrected = spell.existing(corrected.split(' '))
            corrected = spell(' '.join(corrected))
            doc = nlp(corrected)
            nouns = set([token.lemma_ for token in doc if token.pos_ == "NOUN" and 'Case=Nom' in token.morph])
            filtered = [word for word in nouns if word not in reduced_topics]
            return filtered

        # add topics to graph
        # get topic words
        # topic_words, word_scores, topic_nums = model.get_topics()
        # tw_list = []
        # for i, topic in enumerate(topic_words):
        #     tw_list.extend(topic)
        #
        # topics = get_corrected_topics(tw_list)
        # for topic in topics:
        #     my_graph.add((URIRef(f'{voc}/tag/{topic}'), RDF.type, URIRef(voc + 'Тег')))
        # my_graph.serialize(destination=str(settings.BASE_DIR / "ontology.ttl"), format="turtle")

        doc_topics, doc_dist, topic_words, topic_word_scores = model.get_documents_topics(doc_ids=document_ids)
        for i, doc_id in enumerate(document_ids):
            # Get the topic numbers and topic words for the current document
            current_topic_words = topic_words[i]

            # Print the document ID and its corresponding topics
            wr = WebResource.objects.get(id=doc_id)
            filtered = get_corrected_topics(current_topic_words)
            # print(f"Заголовок: {wr.title}")
            # print('\n'.join(filtered))
            # print('---------------')
#             add relations with topics to the RDF graph
            if len(filtered) != 0:
                for topic_word in filtered:
                    tag_url = f'{oogleg_voc}tag/{topic_word}'
                    my_graph.add((URIRef(tag_url), RDF.type, URIRef(oogleg_voc + 'Тег')))
                    my_graph.add((URIRef(wr.url), URIRef(f'{oogleg_voc}має_тег'), URIRef(tag_url)))
                if i % 100 == 0:
                    print(f"Processed {i} documents")
                    my_graph.serialize()




#         spell = Speller('uk')
#
#         for i, topic in enumerate(topic_words):
#
#             print(f"Topic {i}:")
#             # nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN" and 'Case=Nom' in token.morph]
#
#             corrected = spell(' '.join(topic))
#             doc = nlp(corrected)
#             nouns = [token.lemma_ for token in doc if token.pos_ == "NOUN" and 'Case=Nom' in token.morph]
#
#             print("Top Words:", [topic_word for topic_word in topic if topic_word in nouns])
#             num_documents = model.get_topic_sizes(i)
#             document_ids, _ = model.search_documents_by_topic(i)
#             print("Top Web Resources:")
#             for doc in document_ids:
#                 print(doc)
#



