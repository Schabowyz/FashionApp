from django.core.paginator import Paginator

from .models import Item



def items_page(request, page_number):
    items = Item.objects.all()
    paginator = Paginator(items, 24)
    page = paginator.get_page(page_number)
    return page