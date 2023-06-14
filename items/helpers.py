from django.core.paginator import Paginator
from django.db.models import Q

from .models import Item



def items_page(page_number, gender_filters, category_filters, search):
    if not gender_filters and not category_filters and not search:
        items = Item.objects.all()
    else:
        query = Q()
        if gender_filters:
            query.add(Q(gender__in=gender_filters), Q.OR)
        if category_filters:
            query.add(Q(category__in=category_filters), Q.AND)
        if search:
            query.add(Q(name__icontains=search), Q.AND)
        items = Item.objects.filter(query)
    paginator = Paginator(items, 24)
    page = paginator.get_page(page_number)
    return page

def get_genders_dict():
    genders = {}
    pos_genders = Item.GENDERS
    for gender in pos_genders:
        genders[gender[0]] = False
    return genders

def get_categories_dict():
    categories = {}
    pos_categories = Item.CATEGORIES
    for category in pos_categories:
        categories[category[0]] = False
    return categories