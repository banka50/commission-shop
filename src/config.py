import os
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


def _load_toml(path: str) -> dict:
    """Загружает TOML-файл конфигурации, возвращает пустой dict если файл не найден."""
    if not os.path.exists(path):
        return {}
    with open(path, 'rb') as f:
        return tomllib.load(f)


def _get(env_key: str, toml_section: dict, toml_key: str, default: str) -> str:
    """Возвращает значение с приоритетом: env var > config-файл > default."""
    return os.environ.get(env_key) or toml_section.get(toml_key, default)


def _build_uri(toml: dict) -> str:
    db_section = toml.get('database', {})
    engine = _get('DB_ENGINE', db_section, 'engine', 'postgresql')

    if engine == 'postgresql':
        pg = db_section.get('postgresql', {})
        user     = _get('POSTGRES_USER',     pg, 'user',     'postgres')
        password = _get('POSTGRES_PASSWORD', pg, 'password', 'root')
        host     = _get('POSTGRES_HOST',     pg, 'host',     '127.0.0.1')
        port     = _get('POSTGRES_PORT',     pg, 'port',     '5432')
        db       = _get('POSTGRES_DB',       pg, 'db',       'db')
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'

    if engine == 'mysql':
        my = db_section.get('mysql', {})
        user     = _get('MYSQL_USER',     my, 'user',     'root')
        password = _get('MYSQL_PASSWORD', my, 'password', 'root')
        host     = _get('MYSQL_HOST',     my, 'host',     '127.0.0.1')
        port     = _get('MYSQL_PORT',     my, 'port',     '3306')
        db       = _get('MYSQL_DB',       my, 'db',       'db')
        return f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'

    # sqlite
    sq = db_section.get('sqlite', {})
    db_path = _get('SQLITE_PATH', sq, 'path', 'commission_shop.db')
    return f'sqlite:///{db_path}'


_config_path = os.environ.get('CONFIG_FILE', os.path.join(os.path.dirname(__file__), 'config.toml'))
_toml = _load_toml(_config_path)
_app_section = _toml.get('app', {})


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = _get('SECRET_KEY', _app_section, 'secret_key', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = _build_uri(_toml)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 МБ
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
