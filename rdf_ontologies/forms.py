from django import forms
from rdflib import RDF, OWL

from rdf_ontologies.RDF_graph import my_graph


class OntologyPredicatesAddForm(forms.Form):
    predicate_name = forms.CharField(label='Назва предикату', max_length=100)


class OntologyTagsAddForm(forms.Form):
    tag_name = forms.CharField(label='Назва тегу', max_length=100)


class OntologyClassesAddForm(forms.Form):
    class_name = forms.CharField(label='Назва класу', max_length=100)
    parent_class = forms.ChoiceField(label='Батьківський клас', choices=(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_class'].choices = [(str(pc), str(pc)) for pc in my_graph.subjects(RDF.type, OWL.Class)]
