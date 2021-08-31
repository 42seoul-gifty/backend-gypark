from django_filters import (
    FilterSet,
    NumberFilter,
)


class ProductFilter(FilterSet):
    price = NumberFilter(field_name='price__value')
    age_min = NumberFilter(field_name='age__min')
    age_max = NumberFilter(field_name='age__max')
