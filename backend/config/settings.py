import os
import sys
from pathlib import Path


def _bundle_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _data_dir() -> Path:
    override = os.environ.get("SOMNIA_DATA")
    if override:
        path = Path(override)
        path.mkdir(parents=True, exist_ok=True)
        return path
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "Somnia"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "Somnia"
    root.mkdir(parents=True, exist_ok=True)
    return root


BASE_DIR = _bundle_dir()
DATA_DIR = _data_dir()
DESKTOP = os.environ.get("SOMNIA_DESKTOP") == "1"

SECRET_KEY = os.environ.get("SOMNIA_SECRET_KEY", "change-me-in-production")
DEBUG = not DESKTOP
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
FRONTEND_DIR = Path(os.environ.get("SOMNIA_FRONTEND") or (BASE_DIR.parent / "dist" if not getattr(sys, "frozen", False) else BASE_DIR / "frontend"))

INSTALLED_APPS = [
    "simpleui",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "hotel.apps.HotelConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "somnia_django.db",
    }
}

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = DATA_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = DATA_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5174",
]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_DEFAULT_THEME = "admin.lte.css"
SIMPLEUI_HOME_QUICK = True
SIMPLEUI_HOME_ACTION = True
SIMPLEUI_LOGO = ""
SIMPLEUI_CONFIG = {
    "system_keep": False,
    "menu_display": ["数字孪生", "前台账号", "认证与授权"],
    "dynamic": False,
    "menus": [
        {
            "name": "数字孪生",
            "icon": "fas fa-hotel",
            "models": [
                {"name": "住户偏好", "icon": "fas fa-user-check", "url": "/admin/hotel/guest/"},
                {"name": "客户选房", "icon": "fas fa-door-open", "url": "/admin/hotel/gueststay/"},
                {"name": "上传流水", "icon": "fas fa-stream", "url": "/admin/hotel/guestupload/"},
                {"name": "服务需求", "icon": "fas fa-clipboard-list", "url": "/admin/hotel/guestservicechoice/"},
                {"name": "客房实景", "icon": "fas fa-bed", "url": "/admin/hotel/room/"},
                {"name": "酒店服务目录", "icon": "fas fa-concierge-bell", "url": "/admin/hotel/hotelservice/"},
                {"name": "仿真状态", "icon": "fas fa-wave-square", "url": "/admin/hotel/hotelmeta/"},
            ],
        },
        {
            "name": "前台账号",
            "icon": "fas fa-id-card",
            "models": [
                {"name": "客户账号", "icon": "fas fa-user", "url": "/admin/hotel/guestaccount/"},
                {"name": "酒店管理员账号", "icon": "fas fa-user-tie", "url": "/admin/hotel/manageraccount/"},
                {"name": "数据后台账号", "icon": "fas fa-user-shield", "url": "/admin/hotel/backendaccount/"},
                {"name": "发信设置", "icon": "fas fa-envelope", "url": "/admin/hotel/hotelmeta/"},
            ],
        },
        {
            "name": "认证与授权",
            "icon": "fas fa-user-shield",
            "models": [
                {"name": "后台用户", "icon": "fas fa-user", "url": "/admin/auth/user/"},
            ],
        },
    ],
}
