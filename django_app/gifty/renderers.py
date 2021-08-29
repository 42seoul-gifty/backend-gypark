from rest_framework.renderers import JSONRenderer


class DefaultJSONRenderer(JSONRenderer):
    def is_available_value(self, data):
        return isinstance(data, bool) or bool(data) == True

    def render_success(self, data, renderer_context):
        return renderer_context['response'].status_code == 200 and \
               'errors' not in data.keys()

    def render_message(self, data):
        message = data.pop('errors', None)
        message = data.pop('message', message)
        message = data.pop('detail', message)
        return self.flat_message(message)

    def flat_message(self, message):
        if not message:
            return message

        if isinstance(message, str):
            return message

        if isinstance(message, dict):
            return '\n'.join([f'{key}: {self.flat_message(val)}' for key, val in message.items()])

        if isinstance(message, list):
            return ', '.join(message)

        return str(message)

    def wrap_data(self, data, renderer_context):
        data = data or {}

        renderer_context = renderer_context or {}
        success = self.render_success(data, renderer_context)
        message = self.render_message(data)

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
