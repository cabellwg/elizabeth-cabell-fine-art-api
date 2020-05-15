from docker_secrets import get_docker_secret


def safe_execute(default, exception, function, *args):
    """Inline exception handling"""
    try:
        return function(*args)
    except exception:
        return default


class Config:
    """Settings for all environments"""
    MONGO_URI = "mongodb://elizabeth-cabell-fine-art-db:27017/primary"
    BCRYPT_HANDLE_LONG_PASSWORDS = True


class ProdConfig(Config):
    """Production settings"""
    DEBUG = False
    TESTING = False
    ALLOWED_ORIGINS = ["https://elizabethcabellfineart.com",
                       "https://www.elizabethcabellfineart.com"]
    SECRET_KEY = safe_execute(None, ValueError, get_docker_secret, "secret-key")
    JWT_SECRET_KEY = safe_execute(None, ValueError, get_docker_secret, "jwt-secret-key")


class TestConfig(Config):
    """Test settings"""
    DEBUG = True
    TESTING = True
    ALLOWED_ORIGINS = ["*"]
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"


class DevConfig(Config):
    """Development settings"""
    DEBUG = True
    TESTING = True
    ALLOWED_ORIGINS = ["*"]
    SECRET_KEY = "dev-secret-key"
    JWT_SECRET_KEY = "dev-jwt-secret-key"

