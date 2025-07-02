# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
import logging


@shared_task
def send_welcome_email(user_id):
    # logica per inviare email a user_id
    user = User.objects.get(id=user_id)
    send_mail(
        'Benvenuto!',
        'Grazie per esserti registrato.',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )

    user.last_login = timezone.now()
    user.save()

    logging.info(f"Welcome email sent to user {user_id}")

    return f"Welcome email sent to user {user_id}"
