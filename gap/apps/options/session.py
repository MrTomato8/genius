from apps.options.models import OptionChoice


class OptionsSession(object):
    SESSION_KEY = 'options_sessiondata'

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

    def reset_custom_size(self, width=0, height=0):
        self.set('custom_size', {'width': width, 'height': height})

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
