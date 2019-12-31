from django import template

register = template.Library()

@register.filter(name='inlist')
def inlist(value, items):
	return True if value in items else False
