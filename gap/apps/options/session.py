from apps.options.models import OptionChoice
from apps.options import utils


class OptionsSession(object):
    SESSION_KEY = 'options_sessiondata'
    DEFAULT_CHOICE_DATA = {
        utils.custom_size_option_name(): {'width': 0, 'height': 0}
    }

    def __init__(self, request):
        self.request = request
        if self.SESSION_KEY not in request.session:
            request.session[self.SESSION_KEY] = {}
        self.session = request.session[self.SESSION_KEY]

    def get(self, key, default=None):
        if key in self.request.session[self.SESSION_KEY]:
            return self.request.session[self.SESSION_KEY][key]

        return default

    def set(self, key, value):
        self.request.session[self.SESSION_KEY][key] = value
        self.request.session.modified = True

    def valid(self, product):
        return self.get('product') == product.pk

    def reset_product(self, product):
        self.set('product', product.pk)

    def reset_choices(self, choices=None):
        if choices is None:
            choices = {}  # workaround for common python gotcha
        self.set('choices', choices)

    def reset_quantity(self, quantity=0):
        self.set('quantity', quantity)

    def reset_choice_data(self, choice_data=None):
        if choice_data is None:
            choice_data = self.DEFAULT_CHOICE_DATA
        self.set('choice_data', choice_data)

    def update_choice_data(self, data):
        if 'choice_data' in self.request.session[self.SESSION_KEY]:
            choice_data = self.request.session[self.SESSION_KEY]['choice_data']
            choice_data.update(data)
        else:
            self.request.session[self.SESSION_KEY]['choice_data'] = data

    def get_choice_data(self):
        return self.get('choice_data', self.DEFAULT_CHOICE_DATA)

    def get_choice_data_custom_size(self):
        default_custom_size = self.DEFAULT_CHOICE_DATA.get(
            utils.custom_size_option_name(), {})

        return self.get_choice_data().get(
            utils.custom_size_option_name(), default_custom_size)

    def set_choice_data_custom_size(self, data):
        self.update_choice_data({utils.custom_size_option_name(): data})

    # TODO: Return QuerySet, not list
    def get_choices(self):
        choices = []

        s_choices = self.get('choices', {})

        for key in sorted(s_choices.iterkeys()):
            choices.append(OptionChoice.objects.get(pk=s_choices[key]))

        return choices

    def get_quantity(self):
        try:
            return int(self.get('quantity', 0))
        except ValueError:
            return 0
        except TypeError:
            return 0


class OptionsSessionMixin(object):

    def dispatch(self, request, *args, **kwargs):

        self.session = OptionsSession(request)
        return super(OptionsSessionMixin, self).dispatch(
            request, *args, **kwargs)
