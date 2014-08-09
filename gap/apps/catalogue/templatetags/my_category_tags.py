from django import template
from django.db.models import Count
from oscar.templatetags.category_tags import CategoryTreeNode as OscarCategoryTreeNode


register = template.Library()


@register.tag(name="my_category_tree")
def do_category_list(parse, token):
    tokens = token.split_contents()
    error_msg = ("%r tag uses the following syntax: {%% category_tree "
                 "[depth=n] as categories %%}" % tokens[0])
    depth_var = '1'

    if len(tokens) == 4:
        if tokens[2] != 'as':
            raise template.TemplateSyntaxError(error_msg)
        depth_var = tokens[1].split('=')[1]
        as_var = tokens[3]
    elif len(tokens) == 3:
        if tokens[1] != 'as':
            raise template.TemplateSyntaxError(error_msg)
        as_var = tokens[2]
    else:
        raise template.TemplateSyntaxError(error_msg)

    return CategoryTreeNode(depth_var, as_var)


class CategoryTreeNode(OscarCategoryTreeNode):
    def get_category_queryset(self, depth):
        return super(CategoryTreeNode, self).get_category_queryset(depth).annotate(products_count=Count('product'))
