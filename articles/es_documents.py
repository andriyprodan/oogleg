from elasticsearch_dsl import Document, Text, Keyword

# not used
class ArticleDocument(Document):
    title = Text()
    abstract = Text()
    content = Text()
    tags = Keyword()

    class Index:
        name = 'articles'
        settings = {
            "number_of_shards": 2,
        }

