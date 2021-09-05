from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    verbose_name = '회원'

    def ready(self):
        import user.signals
