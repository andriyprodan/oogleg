from neo4j import GraphDatabase
from neo4j.exceptions import AuthError

uri = "bolt://localhost:7687"  # Replace with your Neo4j URI
username = "neo4j"     # Replace with your Neo4j username
password = "admin123"

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
except AuthError as e:
    raise e

