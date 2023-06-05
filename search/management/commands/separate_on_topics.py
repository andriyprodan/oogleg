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
from search.topics_separator import topics_model, get_corrected_topics


class Command(BaseCommand):

    def handle(self, *args, **options):

        document_ids = []
        for wr in WebResource.objects.all():
            document_ids.append(wr.id)

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

        doc_topics, doc_dist, topic_words, topic_word_scores = topics_model.get_documents_topics(doc_ids=document_ids)
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



