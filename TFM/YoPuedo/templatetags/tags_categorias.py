from django import template

register = template.Library()


@register.simple_tag
def categoria_valor(value):
    if value == "Todas categorías":
        return "todas"
    elif value == "Ahorro":
        return "economia"
    elif value == "Conocimientos":
        return "inteligencia"
    elif value == "Deporte":
        return "salud"
    elif value == "Miedos":
        return "mente"


@register.simple_tag
def valor_categoria(value):
    if value == "todas":
        return "Todas categorías"
    elif value == "economia":
        return "Ahorro"
    elif value == "inteligencia":
        return "Conocimientos"
    elif value == "salud":
        return "Deporte"
    elif value == "mente":
        return "Miedos"
