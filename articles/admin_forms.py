from django import forms
from rdflib import RDF, OWL, URIRef, Namespace

from articles.models import WebResource
from rdf_ontologies.RDF_graph import my_graph


class WebResourceForm(forms.ModelForm):
    owl_class = forms.ChoiceField(label='Клас в онтології', choices=(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owl_class'].choices = [(None, '----------------')]
        self.fields['owl_class'].choices.extend([(str(pc), str(pc)) for pc in my_graph.subjects(RDF.type, OWL.Class)])
        if self.instance:
            owl_class = my_graph.value(URIRef(self.instance.url), RDF.type)
            if owl_class:
                self.fields['owl_class'].initial = str(owl_class)

    class Meta:
        model = WebResource
        fields = '__all__'
