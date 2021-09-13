from ..models import Order


def get_dummy_order(**kwargs):
    kwargs.setdefault('user_id', 1)
    kwargs.setdefault('giver_name', '보내는 사람 이름')
    kwargs.setdefault('giver_phone', '보내는 사람 번호')
    kwargs.setdefault('price_id', 1)

    gender_ids = kwargs.pop('gender_ids', [1])
    age_ids = kwargs.pop('age_ids', [1])

    order = Order.objects.create(**kwargs)

    order.gender.add(*gender_ids)
    order.age.add(*age_ids)

    return order
