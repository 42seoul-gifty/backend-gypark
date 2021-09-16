from ..models import (
    Address,
    Order,
    Receiver,
)


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


def get_dummy_receiver(**kwargs):
    kwargs.setdefault('order_id', 1)
    kwargs.setdefault('name', '받는 사람 이름')
    kwargs.setdefault('phone', '받는 사람 번호')

    return Receiver.objects.create(**kwargs)


def get_dummy_address(**kwargs):
    kwargs.setdefault('address', '주소')
    kwargs.setdefault('detail', '상세주소')
    kwargs.setdefault('post_code', '우편번호')
    kwargs.setdefault('receiver_id', 1)

    return Address.objects.create(**kwargs)
