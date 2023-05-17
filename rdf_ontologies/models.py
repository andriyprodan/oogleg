from django.db import models


# Create your models here.
class URLOntology(models.Model):
    name = models.CharField(max_length=255, verbose_name='Назва онтології', null=True, blank=True)
    file = models.FileField(upload_to='rdf_ontologies', verbose_name='Файл онтології')

    class Meta:
        verbose_name = 'Онтологія посилання'
        verbose_name_plural = 'Онтології посилання'

