from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email_with_template(mail_subject, template_name, context, to_emails):
    message = render_to_string(template_name, context)
    text_content = strip_tags(message)
    msg = EmailMultiAlternatives(
        mail_subject,
        text_content,
        settings.EMAIL_HOST_USER,
        to_emails,
    )
    msg.attach_alternative(message, "text/html")
    print(msg)
    msg.send()
