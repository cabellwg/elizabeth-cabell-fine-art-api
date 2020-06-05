import os
import sys


def read_secret(secret_name):
    if secret_name is None:
        print("Missing secret definition", file=sys.stderr)
        return None
    with open("/run/secrets/" + secret_name) as s:
        secret = s.read().strip()
        if secret == "":
            print("Empty secret {}".format(secret_name))
        return secret


class Config:
    """Settings for all environments"""
    DEBUG = True
    TESTING = True
    ALLOWED_ORIGINS = ["*"]
    MONGO_URI = "mongodb://db:27017/primary"
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    IMAGE_STORE_DIR = "./test-img-store"
    SENTRY_DSN = "https://d1abe2a1db2848f8bab4bf37735d3b05@o395084.ingest.sentry.io/5259410"


class ProdConfig(Config):
    """Production settings"""
    DEBUG = False
    TESTING = False
    ALLOWED_ORIGINS = ["https://elizabethcabellfineart.com",
                       "https://www.elizabethcabellfineart.com"]
    SECRET_KEY = read_secret(os.environ.get("SECRET_KEY_SECRET"))
    JWT_SECRET_KEY = read_secret(os.environ.get("JWT_SECRET_KEY_SECRET"))
    IMAGE_STORE_DIR = os.environ.get("IMAGE_STORE_DIR")


class TestConfig(Config):
    """Test settings"""
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"


class DevConfig(Config):
    """Development settings"""
    SECRET_KEY = "dev-secret-key"
    JWT_SECRET_KEY = "dev-jwt-secret-key"
