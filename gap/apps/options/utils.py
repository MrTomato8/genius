from apps.pricelist.models import Price, OptionChoice
from apps.options.models import OptionPicker


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
