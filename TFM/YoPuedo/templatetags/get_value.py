from django import template

register = template.Library()

# Función obtención de valor de un diccionario
@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key) if key in dictionary else ""

# Función concatenación de strings
@register.filter(name='addvalue')
def add_value(value1, value2):
    return str(value1) + str(value2)
