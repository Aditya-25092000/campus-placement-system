"""Authentication service for admin login."""
from werkzeug.security import generate_password_hash, check_password_hash
from db import execute_query, execute_update


def seed_admin():
    """Seed the default admin user if not already present with valid hash."""
    admin = execute_query(
        "SELECT admin_id, password_hash FROM admin_users WHERE username = %s",
        ('admin',), fetchone=True
    )
    if not admin or admin['password_hash'] == 'SEEDED_BY_APP':
        hashed = generate_password_hash('admin123')
        if admin:
            execute_update(
                "UPDATE admin_users SET password_hash = %s WHERE username = %s",
                (hashed, 'admin')
            )
        else:
            execute_update(
                "INSERT INTO admin_users (username, password_hash, full_name, email) "
                "VALUES (%s, %s, %s, %s)",
                ('admin', hashed, 'Administrator', 'admin@campus.edu')
            )


def authenticate(username, password):
    """Authenticate admin user. Returns admin dict or None."""
    admin = execute_query(
        "SELECT * FROM admin_users WHERE username = %s",
        (username,), fetchone=True
    )
    if admin and check_password_hash(admin['password_hash'], password):
        return admin
    return None
