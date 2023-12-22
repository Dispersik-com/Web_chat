import os
from pathlib import Path

# Будуємо шляхи в межах проекту так: BASE_DIR / 'підкаталог'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Налаштування швидкого розгортання - не підходить для продукції
# Див. https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: Зберігайте секретний ключ використовуваний в продакшні у секреті!
SECRET_KEY = 'django-insecure-ym-!s0r2r1pxo3g*1m#k1fgvq@8_gmf%t%%0h5d@#+#cg$^um1'

# SECURITY WARNING: Не запускайте DEBUG включеним в продакшні!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '192.168.0.104']

# Визначення додатків

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar', # Для перегляду запитів
    'rest_framework',
    'rest_framework.authtoken',  # після додавання зробити міграцію - migrate
    'channels',
    'appchat.apps.AppchatConfig',
]

# Створення каналів для веб-сокетів
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # Також можна використовувати Redis
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'appchat.middleware.MiddlewareClass',
]

INTERNAL_IPS = [
    '127.0.0.1',
    # '192.168.0.102',
]

# Для збереження кешу на сервері
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'Webchat_cache'),
    }
}

ROOT_URLCONF = 'MustHaveChat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MustHaveChat.wsgi.application'

ASGI_APPLICATION = 'MustHaveChat.asgi.application'

# База даних
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Перевірка паролів
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Посилання на модель для використання функцій аутентифікації (login, logout)
# Обов'язково має успадковуватися від AbstractBaseUser
AUTH_USER_MODEL = 'appchat.UserProfile'

LOGIN_URL = '/login/'  # Ім'я url для авторизації

# Міжнароднізація
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Статичні файли (CSS, JavaScript, зображення)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


# Призначення шляхів для статичних файлів css, js, img і т.д.
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = []

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Тип поля за замовчуванням
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 5,

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # Всі api доступні тільки авторизованим користувачам
        # 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # авторизація за токенами
        'rest_framework.authentication.TokenAuthentication',
        # Стандартна авторизація (через cookie)
        # Можна комбінувати, але важливий порядок
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',

    ],
}
