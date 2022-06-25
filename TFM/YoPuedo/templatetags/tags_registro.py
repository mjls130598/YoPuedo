from tempfile import template

register = template.Library()


@register.simple_tag
def password_imagen(value):
    if value == "montaña":
        return "Mtñ1."
    elif value == "mirador":
        return "mRd!2"
    elif value == "bosque":
        return "3bsQ?"
    elif value == "piscina":
        return "*4PCn"
    elif value == "playa":
        return "_PlY5"
    elif value == "selva":
        return "Sl6/a"
