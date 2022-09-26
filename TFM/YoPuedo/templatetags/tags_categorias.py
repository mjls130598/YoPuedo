from django import template

register = template.Library()


@register.simple_tag
def categoria_valor(value):
    if value == "Todas categorias":
        return "todas"
    elif value == "Ahorro":
        return "economia"
    elif value == "Conocimientos":
        return "inteligencia"
    elif value == "Deporte":
        return "salud"
    elif value == "Miedos":
        return "mente"
