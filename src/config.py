import os


class Config:
    DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql')

    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def _build_uri() -> str:
        engine = os.environ.get('DB_ENGINE', 'postgresql')

        if engine == 'postgresql':
            user = os.environ.get('POSTGRES_USER', 'postgres')
            password = os.environ.get('POSTGRES_PASSWORD', 'root')
            host = os.environ.get('POSTGRES_HOST', '127.0.0.1')
            port = os.environ.get('POSTGRES_PORT', '5432')
            db = os.environ.get('POSTGRES_DB', 'db')
            return f'postgresql://{user}:{password}@{host}:{port}/{db}'

        if engine == 'mysql':
            user = os.environ.get('MYSQL_USER', 'root')
            password = os.environ.get('MYSQL_PASSWORD', 'root')
            host = os.environ.get('MYSQL_HOST', '127.0.0.1')
            port = os.environ.get('MYSQL_PORT', '3306')
            db = os.environ.get('MYSQL_DB', 'db')
            return f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'

        # sqlite по умолчанию
        db_path = os.environ.get('SQLITE_PATH', 'commission_shop.db')
        return f'sqlite:///{db_path}'

    SQLALCHEMY_DATABASE_URI = _build_uri.__func__()
