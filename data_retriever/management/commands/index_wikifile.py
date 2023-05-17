from django.core.management import BaseCommand
import xml.etree.ElementTree as ET

from articles.models import WebResource
from neo4j_admin.driver import driver


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        tree = ET.parse(options['file_path'])
        root = tree.getroot()
        for doc in root:
            root_wr, _ = WebResource.objects.update_or_create(url=doc.find('url').text,
                                                              defaults={'title': doc.find('title').text,
                                                                        'content': doc.find(
                                                                            'abstract').text,
                                                                        'abstract': doc.find('title').text + doc.find(
                                                                            'abstract').text})
            # for child_link in doc.find('links'):
            #     child_wr, _ = WebResource.objects.update_or_create(url=doc.find('url').text, defaults={'title': child_link.text,
            #                                                                          'content': child_link.text,
            #                                                                          'abstract': child_link.text})
            # #     create connection between root and child in neo4j
            #     with driver.session() as session:
            #         parameters = {
            #             'root_url': root_wr.url,
            #             'child_url': child_wr.url
            #         }
            #         query = """
            #             MATCH (root:WebResource {url: $root_url})
            #             MATCH (child:WebResource {url: $child_url})
            #             MERGE (root)-[:ПОВ'ЯЗАНИЙ_З]->(child)
            #             MERGE (child)-[:ДОЧІРНЯ_СИЛКА]->(root)
            #         """
            #         session.run(query, parameters=parameters)
