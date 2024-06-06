from setuptools import setup, find_packages

setup(
    name='shop',  # Имя вашего проекта
    version='0.1',  # Версия вашего проекта
    packages=find_packages(),  # Найти все пакеты в проекте автоматически
    include_package_data=True,  # Включить данные пакета, такие как шаблоны и статические файлы
    install_requires=[
        'asgiref==3.8.1',
        'crispy-bootstrap5==2024.2',
        'Django==5.0.6',
        'django-cors-headers==4.3.1',
        'django-crispy-forms==2.1',
        'djangorestframework==3.15.1',
        'djangorestframework-simplejwt==5.3.1',
        'drf-yasg==1.21.7',
        'inflection==0.5.1',
        'packaging==24.0',
        'Pillow==10.3.0',
        'psycopg2==2.9.9',
        'PyJWT==2.8.0',
        'pytz==2024.1',
        'PyYAML==6.0.1',
        'sqlparse==0.5.0',
        'typing-extensions==4.11.0',
        'tzdata==2024.1',
        'uritemplate==4.1.1',
        # Добавьте сюда другие зависимости вашего проекта
    ],
)