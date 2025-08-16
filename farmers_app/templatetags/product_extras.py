from django import template

register = template.Library()

@register.filter
def avg_rating(reviews):
    if not reviews:
        return 0
    total = sum([review.rating for review in reviews])
    return round(total / len(reviews))


