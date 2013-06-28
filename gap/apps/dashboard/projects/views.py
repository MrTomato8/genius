from django.views.generic import ListView, DetailView, UpdateView, FormView
from django.db.models.loading import get_model

Order = get_model('order', 'Order')

GROUP_SMALL = 'small'
GROUP_LARGE = 'large'
GROUP_EXHIBITION = 'exhibition'

class ProjectListView(ListView):
    model = Order
    template_name = 'dashboard/projects/project_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(ProjectListView, self).get_context_data(**kwargs)
        user = self.request.user
        groups = user.groups.values_list('name', flat=True)

        if user.is_superuser:
            ctx['orders'] = self.model.objects.all()
        elif GROUP_LARGE in groups:
            ctx['orders'] = self.model.large.all()
        elif GROUP_SMALL in groups:
            ctx['orders'] = self.model.small.all()
        elif GROUP_EXHIBITION in groups:
            ctx['orders'] = self.model.exhibition.all()

        ctx['staff_breadcrumb'] = self.get_breadcrumb(user, groups)
        return ctx

    def get_breadcrumb(self, user, groups):
        if user.is_superuser:
            return "All Teams"

        if GROUP_LARGE in groups:
            return 'Large Format Digital Team'
        elif GROUP_SMALL in groups:
            return ' Small Format Digital Team'
        elif GROUP_EXHIBITION in groups:
            return 'Exhibition Format Digital Team'
        return ''

class ProjectDetailView(DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'dashboard/projects/project_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super(ProjectDetailView, self).get_context_data(**kwargs)
        ctx['exhibition'] = self.object.get_exhibition_lines()
        ctx['small'] = self.object.get_small_lines()
        ctx['large'] = self.object.get_large_lines()
        return ctx



class ProjectLineItemDetailView(DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'dashboard/projects/project_line_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super(ProjectLineItemDetailView, self).get_context_data(**kwargs)
        ctx['order'] = self.object.lines.filter(id=self.kwargs['line_id'])
        return ctx