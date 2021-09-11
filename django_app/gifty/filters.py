from django_filters import (
    FilterSet,
    ModelMultipleChoiceFilter,
    ModelChoiceFilter
)

from .models import (
    AgeCategory,
    GenderCategory,
    PriceCategory
)


class ProductFilter(FilterSet):
    price = ModelChoiceFilter(
        field_name='price',
        queryset=PriceCategory.objects.actived()
    )
    age = ModelMultipleChoiceFilter(
        field_name='age',
        queryset=AgeCategory.objects.actived()
    )
    gender = ModelMultipleChoiceFilter(
        field_name='gender',
        queryset=GenderCategory.objects.actived()
    )
