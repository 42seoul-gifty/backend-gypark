from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import ErrorDetail


class DefaultJSONRenderer(JSONRenderer):
    def is_available_value(self, data):
        return isinstance(data, list) or isinstance(data, bool) or bool(data)

    def render_success(self, data, renderer_context):
        return renderer_context['response'].status_code // 100 == 2

    def render_message(self, data, success):
        if success:
            return None

        return self.flat_message(data)

    def flat_message(self, message):
        if not message:
            return message

        if isinstance(message, str):
            return message

        if isinstance(message, dict):
            return '\n'.join([f'{key}: {self.flat_message(val)}' for key, val in message.items()])

        if isinstance(message, list):
            return ', '.join(map(lambda item: self.flat_message(item), message))

        return str(message)

    def wrap_data(self, data, renderer_context):
        renderer_context = renderer_context or {}
        success = self.render_success(data, renderer_context)
        message = self.render_message(data, success)
        data = data if success else None

        wrapped = {
            'success': success,
            'message': message,
            'data': data,
        }

        return {key:val for key,val in wrapped.items() if self.is_available_value(val)}

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = self.wrap_data(data, renderer_context)
        return super().render(data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)
