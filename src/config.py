import os


class Config:
    USER = os.environ.get('POSTGRES_USER', 'postgres')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'root')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', '5432')
    DB = os.environ.get('POSTGRES_DB', 'db')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
