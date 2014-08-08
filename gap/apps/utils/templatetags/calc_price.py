from django import template
from apps.options.calc import OptionsCalculator

register = template.Library()


@register.assignment_tag(takes_context=True)
def calc_price(context, qty):
    session = context['session']
    request = context['request']
    calc = OptionsCalculator(context['product'])
    choices = []
    if u'choices' in context:
        choices = context['choices']
    choice_data = session.get_choice_data()
    qty = int(qty)
    prices = calc.calculate_costs(choices, qty, choice_data)
    price = prices.get_price_incl_tax(qty, 1, request.user)[0]
    return price
