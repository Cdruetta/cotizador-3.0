import os

from django.conf import settings
from django.db import connection, OperationalError


def get_db_usage_percent():
    try:
        max_size_mb = float(os.environ.get("DB_USAGE_MAX_MB", "0"))
    except (TypeError, ValueError):
        max_size_mb = 0.0

    engine = settings.DATABASES["default"]["ENGINE"]
    if "sqlite3" in engine:
        db_path = settings.DATABASES["default"]["NAME"]
        if db_path and not os.path.isabs(db_path):
            db_path = os.path.join(str(settings.BASE_DIR), db_path)
        if os.path.exists(db_path):
            db_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2)
            if max_size_mb > 0:
                return round((db_mb / max_size_mb) * 100, 2), db_mb, round(max_size_mb, 2)
            return None, db_mb, round(max_size_mb, 2)
        return None, 0.0, round(max_size_mb, 2)

    if "postgresql" in engine:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(current_database());")
                size_mb = round(cursor.fetchone()[0] / (1024 * 1024), 2)
                if max_size_mb > 0:
                    return round((size_mb / max_size_mb) * 100, 2), size_mb, round(max_size_mb, 2)
                return None, size_mb, round(max_size_mb, 2)
        except OperationalError:
            return None, 0.0, round(max_size_mb, 2)

    return None, 0.0, round(max_size_mb, 2)

