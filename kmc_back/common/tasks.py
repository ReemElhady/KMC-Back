from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from common.utility import send_email_with_template


@shared_task
def async_send_email_with_template(mail_subject, template_name, context, to_emails):
    send_email_with_template(mail_subject, template_name, context, to_emails)


@shared_task
def async_send_email(subject, message, receivers):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=receivers,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
