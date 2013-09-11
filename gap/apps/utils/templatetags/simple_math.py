from django import template
from decimal import Decimal, Context, setcontext
from math import ceil
register = template.Library()

@register.filter
def multiply(value, arg, prec=2):
    """multiply: value * arg"""
    try:
        return round(Decimal(str(value))*Decimal(str(arg)), prec)
    except:
        return Decimal(0)
    
@register.filter
def divide(value, arg, prec=2):
    """divide: value / arg"""
    try:
        return round(Decimal(str(value))/Decimal(str(arg)), prec)
    except:
        return Decimal(0)
@register.filter
def int_multiply(value, arg):
    """multiply: value * arg"""
    return value*arg
@register.filter
def divide_triple(value, arg):
    """divide: value / arg"""
    return divide(value, arg, prec=3)
@register.filter
def divide_int(value,arg):
    v = ceil(value/arg)
    if value != 0 and v == 0:
        v =1
    return v