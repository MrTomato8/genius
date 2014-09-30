from django import template
from oscar.apps.promotions.models import RawHTML

register = template.Library()


@register.simple_tag
def show_content_block(block_name):
    try:
        content_block = RawHTML.objects.get(name=block_name).body
    except RawHTML.DoesNotExist:
        content_block = None
    return content_block
