from django import template
from apps.options import utils
register = template.Library()

@register.filter
def trade_user(user):
    return utils.trade_user(user)