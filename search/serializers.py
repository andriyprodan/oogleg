from rest_framework import serializers

from articles.models import WebResource


class WebResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebResource
        fields = ('url', 'title',)