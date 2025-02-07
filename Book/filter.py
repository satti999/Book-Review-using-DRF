import django_filters
from .models import Book




class BookFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name="author", lookup_expr="icontains")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    class Meta:
        model = Book
        fields = {
            'title': ['iexact','icontains'],
            'author': ['iexact','icontains'],
            'description': ['iexact','icontains'],
        }