from django import template

register = template.Library()


@register.filter
def addsrc(field, src):
    return field.as_widget(attrs={"src": src})
