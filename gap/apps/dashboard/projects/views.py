from django.views.generic import ListView, DetailView, UpdateView, FormView
from django.db.models.loading import get_model

Order = get_model('order', 'Order')


class ProjectListView(ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'dashboard/projects/project_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(ProjectListView, self).get_context_data(**kwargs)
        ctx['exhibition'] = self.model.exhibition.all()
        ctx['small'] = self.model.small.all()
        ctx['large'] = self.model.large.all()
        return ctx

class ProjectDetailView(DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'dashboard/projects/project_detail.html'
