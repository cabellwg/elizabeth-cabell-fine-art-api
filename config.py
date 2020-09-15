import os
import sys
import json


def read_secret(secret_name):
    if secret_name is None:
        if os.environ.get("ENV") == "prod":
            print("Missing secret definition", file=sys.stderr)
        return None
    with open("/run/secrets/" + secret_name) as s:
        secret = s.read().strip()
        if secret == "":
            print("Empty secret {}".format(secret_name))
        return secret


def read_key(key_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    keysfile = os.path.join(dir_path, ".auth_keys.json")
    if not os.path.exists(keysfile):
        if os.environ.get("ENV") == "dev":
            print("Missing .auth_keys.json", file=sys.stderr)
        return None
    with open(keysfile) as keys:
        auth_keys = json.load(keys)
        return auth_keys[key_name]


class Config:
    """Settings for all environments"""
    DEBUG = True
    TESTING = True
    ALLOWED_ORIGINS = ["*"]
    MONGO_URI = "mongodb+srv://ecfa-api-test:{}@elizabeth-cabell-fine-art-05jp7.mongodb.net/test?retryWrites=true&w" \
                "=majority".format(read_key("testDbPass"))
    DB_NAME = "test"
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    IMAGE_STORE_DIR = os.environ.get("IMAGE_STORE_DIR") or "./test-img-store"
    SENTRY_DSN = "https://d1abe2a1db2848f8bab4bf37735d3b05@o395084.ingest.sentry.io/5259410"
    JWT_ACCESS_TOKEN_EXPIRES = 10800


class ProdConfig(Config):
    """Production settings"""
    DEBUG = False
    TESTING = False
    ALLOWED_ORIGINS = ["https://elizabethcabellfineart.com",
                       "https://www.elizabethcabellfineart.com",
                       "https://ecfaprerelease.williamcabell.me"
                       ]
    MONGO_URI = "mongodb+srv://ecfa-api:{}@elizabeth-cabell-fine-art-05jp7.mongodb.net/prod?retryWrites=true&w=maj" \
                "ority".format(read_secret(os.environ.get("DB_PASS_SECRET")))
    DB_NAME = "prod"
    SECRET_KEY = read_secret(os.environ.get("SECRET_KEY_SECRET"))
    JWT_SECRET_KEY = read_secret(os.environ.get("JWT_SECRET_KEY_SECRET"))
    USER_REGISTRATION_CODE = read_secret(os.environ.get("USER_RCODE_SECRET"))
    IMAGE_STORE_DIR = os.environ.get("IMAGE_STORE_DIR")


class TestConfig(Config):
    """Test settings"""
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    USER_REGISTRATION_CODE = "test-registration-code"
    MONGO_URI = "mongodb+srv://fakeuser:fakepass@fake.cluster.net/test?retryWrites=true&w" \
                "=majority"


class DevConfig(Config):
    """Development settings"""
    SECRET_KEY = "dev-secret-key"
    JWT_SECRET_KEY = "dev-jwt-secret-key"
    USER_REGISTRATION_CODE = "dev-registration-code"
