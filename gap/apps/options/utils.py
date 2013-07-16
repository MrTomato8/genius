from apps.pricelist.models import Price, OptionChoice
from apps.options.models import OptionPicker
from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Min


def available_choices(product, picker):
    return OptionChoice.objects.filter(
        option=picker.option,
        prices__in=Price.objects.filter(product=product)).distinct()


def available_pickers(product, group):
    poptions = product.options
    pickers = OptionPicker.objects.filter(group=group)
    if poptions:
        return pickers.filter(option__in=poptions)
    else:
        return pickers


def custom_size_chosen(choices):
    cooption, cchoice = settings.OPTIONCHOICE_CUSTOMSIZE
    try:
        custom_size_choice = OptionChoice.objects.get(
            option__code=cooption, code=cchoice)
    except OptionChoice.DoesNotExist:
        return False
    else:
        return custom_size_choice in choices


def discrete_pricing(product):
    items = Price.objects.filter(product=product).values('quantity').distinct()
    return len(items) > 1


def available_quantities(product, choices):
    result = {}
    prices = Price.objects.filter(product=product)

    for choice in choices:
        prices = prices.filter(option_choices=choice)

    items = prices.values('quantity').distinct()

    for item in items:
        result[item['quantity']] = None

    return result


def trade_user(user):
    try:
        group = Group.objects.get(name=settings.TRADE_GROUP_NAME)
    except Group.DoesNotExist:
        return False

    return group in user.groups.all()


def min_order(product, choices):

    prices = Price.objects.filter(product=product)

    for choice in choices:
        prices = prices.filter(option_choices=choice)

    return prices.aggregate(Min('min_order'))['min_order__min']
