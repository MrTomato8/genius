from django import template
from treebeard.mp_tree import MP_Node

register = template.Library()


@register.filter(name='is_category_active')
def is_category_active(category, main_category):
    """
    Return True, if main_category equal to category or if main_category is
    descendant of category
    """
    if isinstance(main_category, MP_Node):
        cat = category[0]
        if cat == main_category or main_category.is_descendant_of(cat):
            return True
    return False
