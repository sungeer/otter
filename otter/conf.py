import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
config_name = os.getenv('FLASK_CONFIG', 'production')

basedir = Path(__file__).resolve().parent.parent


class BaseConfig:
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

settings = config[config_name]


if __name__ == '__main__':
    print(basedir)
    print(settings.DB_HOST)
