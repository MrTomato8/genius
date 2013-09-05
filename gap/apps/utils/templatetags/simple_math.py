from django import template
from decimal import Decimal, Context, setcontext

register = template.Library()

@register.filter
def multiply(value, arg, prec=2):
    """multiply: value * arg"""
    return round(Decimal(str(value))*Decimal(str(arg)), prec)
    
@register.filter
def divide(value, arg, prec=2):
    """divide: value / arg"""
    return round(Decimal(str(value))/Decimal(str(arg)), prec)
@register.filter
def int_multiply(value, arg):
    """multiply: value * arg"""
    return value*arg
@register.filter
def divide_triple(value, arg):
    """divide: value / arg"""
    return divide(value, arg, prec=3)
