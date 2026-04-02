from django import template

register = template.Library()

@register.filter
def precio_cl(value):
    try:
        return '{:,.0f}'.format(float(value)).replace(',', '.')
    except (ValueError, TypeError):
        return value