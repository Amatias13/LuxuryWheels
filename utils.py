def generate_password_hash(password):
    """Hash a plaintext password using werkzeug's generate_password_hash."""
    from werkzeug.security import generate_password_hash as gen_hash

    return gen_hash(password)


def check_password_hash(hash, password):
    """Check a plaintext password against a hash using werkzeug's check_password_hash."""
    from werkzeug.security import check_password_hash as chk_hash

    return chk_hash(hash, password)
