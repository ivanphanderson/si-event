from django import template
register = template.Library()

@register.filter(name="convert")
def convert(value, honor):
    return int(value/100.0 * honor)
