from django.urls import path

from contact_us.views.contact_us_view import ContactUsAPI

urlpatterns = [
    path('', ContactUsAPI.as_view({
        'get': 'get_contact_us_content',
        'post': 'post_form'
    }), name='contact-us'),
]
