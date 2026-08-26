from rest_framework.pagination import PageNumberPagination


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"  # lets the client request e.g. ?page_size=50
    max_page_size = 100  # hard ceiling — a client can't request an unbounded page