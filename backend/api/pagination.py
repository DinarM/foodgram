from rest_framework.pagination import PageNumberPagination

from foodgram.constants import DEFAULT_PAGE_SIZE


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE
