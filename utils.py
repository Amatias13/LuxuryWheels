def generate_password_hash(password):
    """Hash a plaintext password using werkzeug's generate_password_hash."""
    from werkzeug.security import generate_password_hash as gen_hash

    return gen_hash(password)


def check_password_hash(hash, password):
    """Check a plaintext password against a hash using werkzeug's check_password_hash."""
    from werkzeug.security import check_password_hash as chk_hash

    return chk_hash(hash, password)


def parse_date(s):
    """Parse a date string in either ISO (YYYY-MM-DD) or DD/MM/YYYY formats.

    Returns a `date` object or raises `ValueError` on invalid format.
    """
    from datetime import datetime

    if s is None:
        raise ValueError("Formato de data inválido")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            continue
    raise ValueError("Formato de data inválido")
