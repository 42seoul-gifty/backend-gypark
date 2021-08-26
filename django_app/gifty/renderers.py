from rest_framework.renderers import JSONRenderer


class DefaultJSONRenderer(JSONRenderer):
    def is_available_value(self, data):
        return isinstance(data, bool) or bool(data) == True

    def wrap_data(self, data, renderer_context):
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        success = renderer_context['response'].status_code == 200
        message = data.pop('detail', None)

        data = {
            'success': success,
            'message': message,
            'data': data,
        }

        rm_blank = {key:val for key,val in data.items() if self.is_available_value(val)}

        return rm_blank

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = self.wrap_data(data, renderer_context)
        return super().render(data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
