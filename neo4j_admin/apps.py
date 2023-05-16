from django.apps import AppConfig


class Neo4JAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'neo4j_admin'

    def ready(self):
        import neo4j_admin.driver
