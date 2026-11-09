import math
import random

from django import template

register = template.Library()


@register.simple_tag
def postcards_grid(postcards):
    cards = list(postcards)
    count = len(cards)
    cell_count = (math.isqrt(count - 1) + 1) ** 2
    while len(cards) < cell_count:
        cards.insert(random.choice(range(len(cards) + 1)), None)
    return cards
