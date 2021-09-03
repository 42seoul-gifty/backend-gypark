from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    '^\d{8,11}$',
    '8~11자리의 숫자만 입력할 수 있습니다.'
)
