from django import template

register = template.Library()


@register.simple_tag
def addsrc(field, src):
    return field.as_widget(attrs={"src": src})
