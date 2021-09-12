from django.http import JsonResponse


def handler404(request, *args, **kwargs):
    return JsonResponse({
        'success': False,
        'message': "찾을 수 없는 요청입니다."
    }, status=404)


def handler500(request, *args, **kwargs):
    return JsonResponse({
        'success': False,
        'message': "서버 내부에서 에러가 발생했습니다."
    }, status=500)


def test_500_view(request):
    raise Exception('raise exception')
