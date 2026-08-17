from django import template

register = template.Library()

@register.filter
def formatar_dinheiro(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
        
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f} Mi"
    elif value >= 1_000:
        return f"${value / 1_000:.1f} Mil"
    return f"${value:.2f}"
