from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from apps.options.models import OptionPicker, OptionChoice,Option

class Utils(object):
    costum_size=None
    def __init__(self):
        cooption, cchoice = settings.OPTIONCHOICE_CUSTOMSIZE
        try:
            self.costum_size = OptionChoice.objects.get(
                option__code=cooption, code=cchoice)
        except:
            option, _ = Option.objects.get_or_create(code=cooption)
            self.costum_size = OptionChoice.objects.create(code=cchoice,option=option)

    def custom_size_chosen(self,choices):
        return self.costum_size in choices
utils = Utils()

def custom_size_chosen(choices):
    return utils.custom_size_chosen(choices)

def available_choices(product, picker):
    return OptionChoice.objects.filter(
        option=picker.option,
        prices__in=product.prices.all()).distinct().select_related('option').prefetch_related('conflicts_with')


def available_pickers(product, group):
    poptions = product.options
    pickers = OptionPicker.objects\
        .filter(group=group, # next line is just query count optimization, to exclude unavailable pickers at this phase, without checking it has valid choices in available_choice()
                option__choices__prices__in=product.prices.all())\
        .distinct().select_related('option')
    if poptions:
        return pickers.filter(option__in=poptions)
    else:
        return pickers




def custom_size_option_name():
    return settings.OPTIONCHOICE_CUSTOMSIZE[0]


def custom_size_option_value():
    return settings.OPTIONCHOICE_CUSTOMSIZE[1]


def discrete_pricing(product):
    cnt = product.prices.all().values('quantity').distinct().count()
    return cnt > 1


def trade_user(user):
    try:
        group = Group.objects.get(name=settings.TRADE_GROUP_NAME)
    except Group.DoesNotExist:
        return False

    return user is not None and group in user.groups.all()


# TODO: these may be optimized
def min_order(product, choices):

    prices = product.prices.all()

    for choice in choices:
        prices = prices.filter(option_choices=choice)

    return prices.aggregate(models.Min('min_order'))['min_order__min']


def min_area(product, choices):

    prices = product.prices.all()

    for choice in choices:
        prices = prices.filter(option_choices=choice)

    return prices.aggregate(models.Min('min_area'))['min_area__min']
