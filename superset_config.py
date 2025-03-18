import os

SECRET_KEY = os.getenv("SECRET_KEY", "QKJjP0D0xEPd5d+EokXwWjn0vY80Jeb9B3QN37gSJBXCcX24fLRrZ63P")

SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:JsudmSAXmiWazQtDuBFihhWOMxhZbzzw@autorack.proxy.rlwy.net:43068/superset"
)

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_URL": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
}

ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": ["*"],
    "origins": ["*"],
}

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "CELERY_TASKS": True,
}

#test deploy

