from django import template
from oscar.apps.promotions.models import RawHTML

register = template.Library()


@register.simple_tag
def show_content_block(block_name):
    content_block = RawHTML.objects.get(name=block_name).body
    return content_block
