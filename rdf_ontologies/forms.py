from django import forms


class OntologyPredicatesAddForm(forms.Form):
    predicate_name = forms.CharField(label='Назва предикату', max_length=100)
