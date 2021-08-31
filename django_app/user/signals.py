from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(user_signed_up)
def on_signed_up(request, user, **kwargs):
    if user.socialaccount_set.count() == 0:
        return

    social_account = user.socialaccount_set.all()[0]
    extra_data = social_account.extra_data

    if social_account.provider == 'kakao':
        user.nickname = extra_data['properties']['nickname']

    user.save()
