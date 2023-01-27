from django import template

register = template.Library()


@register.filter(name='addvalue')
def addvalue(field, value):
    return field.as_widget(attrs={"value": value})
