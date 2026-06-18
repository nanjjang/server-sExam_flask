from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import get_user, save_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', body_class='page-auth')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        return render_template('register.html', error='아이디와 비밀번호를 입력해주세요.', body_class='page-auth')

    if get_user(username):
        return render_template('register.html', error='이미 존재하는 아이디입니다.', body_class='page-auth')

    save_user(username, generate_password_hash(password))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', body_class='page-auth')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = get_user(username)
    if not user or not check_password_hash(user['password'], password):
        return render_template('login.html', error='아이디 또는 비밀번호가 올바르지 않습니다.', body_class='page-auth')

    session['user_id'] = username
    return redirect(url_for('root.root'))


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('root.root'))
