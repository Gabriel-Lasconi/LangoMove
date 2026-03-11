import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "airtable.env")

SECRET_KEY = "django-insecure-change-this-later"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",   # add this
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",   # add this
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "login"

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")

AIRTABLE_TABLES = {
    "languages": os.getenv("AIRTABLE_TABLE_LANGUAGES", "languages"),
    "age_groups": os.getenv("AIRTABLE_TABLE_AGE_GROUPS", "age-groups"),
    "topics": os.getenv("AIRTABLE_TABLE_TOPICS", "topics"),
    "courses": os.getenv("AIRTABLE_TABLE_COURSES", "courses"),
    "sessions": os.getenv("AIRTABLE_TABLE_SESSIONS", "sessions"),
    "games": os.getenv("AIRTABLE_TABLE_GAMES", "games"),
    "session_games": os.getenv("AIRTABLE_TABLE_SESSION_GAMES", "session-games"),
    "session_requests": os.getenv("AIRTABLE_TABLE_SESSION_REQUESTS", "session-requests"),
    "vocabulary": os.getenv("AIRTABLE_TABLE_VOCABULARY", "vocabulary"),
    "game_vocabulary": os.getenv("AIRTABLE_TABLE_GAME_VOCABULARY", "game-vocabulary"),
    "phrases": os.getenv("AIRTABLE_TABLE_PHRASES", "phrases"),
    "game_phrases": os.getenv("AIRTABLE_TABLE_GAME_PHRASES", "game-phrases"),
}