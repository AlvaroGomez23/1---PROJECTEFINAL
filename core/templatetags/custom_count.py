from django import template

register = template.Library()

@register.filter
def times(n, total):
    try:
        n = int(n)
        total = int(total)
        from math import ceil
        return range(ceil(total / n))
    except (ValueError, ZeroDivisionError):
        return []