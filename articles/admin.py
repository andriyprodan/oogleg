from django.contrib import admin

from articles.models import WebResource


# Register your models here.
@admin.register(WebResource)
class WebResourceAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'abstract')