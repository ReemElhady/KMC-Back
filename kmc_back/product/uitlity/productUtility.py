from django.core.exceptions import ValidationError

allowed_extensions = ['jpg', 'png', 'jpeg', 'gif', 'svg']
extension_error_message = "allowed format is :  'jpg', 'png', 'jpeg',  'gif','svg' "


def file_size(value):
    limit = 5 * 1024 * 1000
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MiB.')
