from django import template

register = template.Library()

@register.filter
def get_domain_from_url(url):
    return url.split('/')[2]