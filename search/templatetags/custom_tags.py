from django import template

register = template.Library()

@register.filter
def get_domain_from_url(url):
    return url.split('/')[2]

@register.filter
def stringify(value):
    return str(value)