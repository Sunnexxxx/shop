

from django.core.mail import send_mail

send_mail(
    'Тестовое письмо',
    'Это тестовое письмо.',
    'artykovhondamir@gmail.com',
    ['dilafruzartykova@gmail.com'],
    fail_silently=False,
)
