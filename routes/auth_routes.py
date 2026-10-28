"""Authentication routes - login and logout."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.auth_service import authenticate

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html')
        admin = authenticate(username, password)
        if admin:
            session['admin_id'] = admin['admin_id']
            session['admin_name'] = admin['full_name']
            session['admin_username'] = admin['username']
            flash(f'Welcome back, {admin["full_name"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
