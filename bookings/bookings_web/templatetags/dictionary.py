from django.template import Library

register = Library()


@register.filter
def key_value(dict, key):
    return dict[key]