

from django import template

register = template.Library()

@register.filter
def sum_attribute(queryset, attribute):
    return sum(getattr(item, attribute, 0) for item in queryset)
