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

    def reset_choices(self, product):
        self.set('product', product.pk)
        self.set('choices', {})

    def get_choices(self):
        choices = []

        for k, pk in self.get('choices', {}).items():
            choices.append(OptionChoice.objects.get(pk=pk))

        return choices


class OptionsSessionMixin(object):

    def dispatch(self, request, *args, **kwargs):

        self.session = OptionsSession(request)
        return super(OptionsSessionMixin, self).dispatch(
            request, *args, **kwargs)
