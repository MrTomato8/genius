from django.views.generic.base import TemplateView


class PickOptionsView(TemplateView):
    template_name = 'options/pick.html'

    def get_context_data(self, **kwargs):
        return {'msg': 'Hello World'}
