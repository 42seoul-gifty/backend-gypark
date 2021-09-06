from django_filters import (
    FilterSet,
    NumberFilter,
    ModelMultipleChoiceFilter,
)

from .models import (
    AgeCategory,
    GenderCategory
)


class ProductFilter(FilterSet):
    price = NumberFilter(
        field_name='price__value'
    )
    age = ModelMultipleChoiceFilter(
        field_name='age',
        queryset=AgeCategory.objects.all()
    )
    gender = ModelMultipleChoiceFilter(
        field_name='gender',
        queryset=GenderCategory.objects.all()
    )
