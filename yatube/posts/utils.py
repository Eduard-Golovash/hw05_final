from django.core.paginator import Paginator


def paginate(objects, page_number, posts_per_page=10):
    paginator = Paginator(objects, posts_per_page)
    page_obj = paginator.get_page(page_number)
    return paginator, page_obj
