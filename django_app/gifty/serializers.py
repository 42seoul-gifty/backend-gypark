from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    CharField
)

from django.db.models import (
    Max,
    Min
)

from .models import (
    Product,
    AgeCategory,
    PriceCategory,
    GenderCategory,
)
from order.models import Receiver


class ProductSerializer(ModelSerializer):
    price = SerializerMethodField()
    image_url = SerializerMethodField()
    # age_min = SerializerMethodField()
    # age_max = SerializerMethodField()
    # gender = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'detail',
            'price',
            'thumbnail',
            'image_url',
            # 'age_min',
            # 'age_max',
            # 'gender',
        )

    def get_age_min(self, obj):
        return obj.age.aggregate(Min('min'))['min__min']

    def get_age_max(self, obj):
        return obj.age.aggregate(Max('max'))['max__max']

    def get_gender(self, obj):
        return obj.gender.first().name

    def get_price(self, obj):
        return obj.price.value

    def get_image_url(self, obj):
        request = self.context.get('request', None)

        return map(
            lambda obj: request.build_absolute_uri(obj.image.url),
            obj.images.all()
        )


class AgeSerializer(ModelSerializer):
    value = SerializerMethodField()

    class Meta:
        model = AgeCategory
        fields = (
            'id',
            'value',
        )

    def get_value(self, obj):
        return str(obj)


class GenderSerializer(ModelSerializer):
    class Meta:
        model = GenderCategory
        fields = (
            'id',
            'name'
        )


class PriceSerializer(ModelSerializer):
    class Meta:
        model = PriceCategory
        fields = (
            'id',
            'value',
        )


class ProductReactSerializer(Serializer):
    receiver_id = CharField()

