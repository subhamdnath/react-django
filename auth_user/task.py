from celery import shared_task
from .models import *
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


@shared_task
def send_signup_verification_email(email, otp, user_name):
    html_content = render_to_string("home/verify_otp.html", context={"otp": otp, "user_name":user_name})                             
    email = EmailMessage("Email verification", html_content, settings.EMAIL_HOST_USER, [email])
    email.content_subtype = "html"
    email.send()

"""---- command to run celery worker-----"""
"celery -A PROJECT worker -l info" 