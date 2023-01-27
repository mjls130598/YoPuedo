from django import template

register = template.Library()


@register.filter(name='addsrc')
def addsrc(field, src):
    return field.as_widget(attrs={"src": src})
