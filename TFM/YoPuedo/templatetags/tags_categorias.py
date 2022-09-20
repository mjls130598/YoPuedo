from django import template

categoria = template.Library()


@categoria.simple_tag
def categoria_valor(value):
    if value == "Todas categorías":
        return ""
    elif value == "Ahorro":
        return "economia"
    elif value == "Conocimientos":
        return "inteligencia"
    elif value == "Deporte":
        return "salud"
    elif value == "Miedos":
        return "mente"