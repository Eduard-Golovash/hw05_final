from django.core.paginator import Paginator


def paginate(objects, page_number):
    paginator = Paginator(objects, 10)
    page_obj = paginator.get_page(page_number)
    return paginator, page_obj
