from flask import Flask, render_template, request, redirect, session
import mysql.connector
import re

app = Flask(__name__)
app.secret_key = 'secret123'


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="korochki_net"
)


# -----------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# -----------------------------

def fetch_one(query, params=()):
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    return result


def fetch_all(query, params=()):
    cursor = db.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    return result


def execute_query(query, params=()):
    cursor = db.cursor()
    cursor.execute(query, params)
    db.commit()
    cursor.close()


def is_auth():
    return 'user_id' in session


def is_admin():
    return session.get('role_id') == 1


def register_error(message):
    return render_template('register.html', error=message)


# -----------------------------
# ГЛАВНАЯ И ВХОД
# -----------------------------

@app.route('/')
def home():
    return render_template('login.html', error='')


@app.route('/login', methods=['POST'])
def login():
    login_value = request.form['login']
    password_value = request.form['password']

    user = fetch_one(
        "SELECT * FROM users WHERE login = %s AND password_hash = %s",
        (login_value, password_value)
    )

    if not user:
        return render_template('login.html', error='Неверный логин или пароль')

    session['user_id'] = user[0]
    session['login'] = user[4]
    session['role_id'] = user[8]

    if is_admin():
        return redirect('/admin')

    return redirect('/applications')


# -----------------------------
# РЕГИСТРАЦИЯ
# -----------------------------

@app.route('/register')
def register():
    return render_template('register.html', error='')


@app.route('/register_user', methods=['POST'])
def register_user():
    last_name = request.form['last_name'].strip()
    first_name = request.form['first_name'].strip()
    middle_name = request.form['middle_name'].strip()
    login_value = request.form['login'].strip()
    password_value = request.form['password'].strip()
    phone = request.form['phone'].strip()
    email = request.form['email'].strip()

    if len(login_value) < 6:
        return register_error('Логин должен содержать минимум 6 символов')

    if len(password_value) < 8:
        return register_error('Пароль должен содержать минимум 8 символов')

    if not re.fullmatch(r"8\d{10}", phone):
        return register_error('Телефон должен быть в формате 89307087450')

    if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        return register_error('Некорректный email')

    if not re.fullmatch(r"[А-Яа-яЁё]+", last_name):
        return register_error('Фамилия должна быть на кириллице')

    if not re.fullmatch(r"[А-Яа-яЁё]+", first_name):
        return register_error('Имя должно быть на кириллице')

    if middle_name and not re.fullmatch(r"[А-Яа-яЁё]+", middle_name):
        return register_error('Отчество должно быть на кириллице')

    existing_user = fetch_one(
        "SELECT id_user FROM users WHERE login = %s",
        (login_value,)
    )

    if existing_user:
        return register_error('Пользователь с таким логином уже существует')

    execute_query(
        """
        INSERT INTO users 
        (last_name, first_name, middle_name, login, password_hash, phone, email, id_role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            last_name,
            first_name,
            middle_name,
            login_value,
            password_value,
            phone,
            email,
            2
        )
    )

    return redirect('/')


# -----------------------------
# ЗАЯВКИ ПОЛЬЗОВАТЕЛЯ
# -----------------------------

@app.route('/applications')
def applications():
    if not is_auth():
        return redirect('/')

    applications_list = fetch_all(
        """
        SELECT 
            a.id_application,
            a.course_name,
            a.start_date,
            a.payment_method,
            s.status_name,
            a.review
        FROM applications a
        JOIN statuses s ON a.id_status = s.id_status
        WHERE a.id_user = %s
        """,
        (session['user_id'],)
    )

    return render_template('applications.html', applications=applications_list)


@app.route('/create_application', methods=['POST'])
def create_application():
    if not is_auth():
        return redirect('/')

    course_name = request.form['course_name'].strip()
    start_date = request.form['start_date'].strip()
    payment_method = request.form['payment_method'].strip()

    if not course_name:
        return "Введите название курса"

    if payment_method not in ['Наличные', 'Перевод']:
        return "Некорректный способ оплаты"

    execute_query(
        """
        INSERT INTO applications 
        (id_user, course_name, start_date, payment_method, id_status, review)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            session['user_id'],
            course_name,
            start_date,
            payment_method,
            1,
            None
        )
    )

    return redirect('/applications')


@app.route('/add_review', methods=['POST'])
def add_review():
    if not is_auth():
        return redirect('/')

    application_id = request.form['application_id']
    review = request.form['review'].strip()

    application = fetch_one(
        """
        SELECT id_application
        FROM applications
        WHERE id_application = %s 
        AND id_user = %s 
        AND id_status = 3
        """,
        (application_id, session['user_id'])
    )

    if not application:
        return "Отзыв можно оставить только после завершения обучения"

    execute_query(
        "UPDATE applications SET review = %s WHERE id_application = %s",
        (review, application_id)
    )

    return redirect('/applications')


# -----------------------------
# АДМИН-ПАНЕЛЬ
# -----------------------------

@app.route('/admin')
def admin():
    if not is_auth():
        return redirect('/')

    if not is_admin():
        return "Доступ запрещен"

    all_applications = fetch_all(
        """
        SELECT 
            a.id_application,
            u.last_name,
            u.first_name,
            a.course_name,
            a.start_date,
            a.payment_method,
            s.id_status,
            s.status_name,
            a.review
        FROM applications a
        JOIN users u ON a.id_user = u.id_user
        JOIN statuses s ON a.id_status = s.id_status
        ORDER BY a.id_application
        """
    )

    users = fetch_all(
        """
        SELECT id_user, last_name, first_name, login, id_role
        FROM users
        ORDER BY id_user
        """
    )

    return render_template(
        'admin.html',
        applications=all_applications,
        users=users
    )


@app.route('/update_status', methods=['POST'])
def update_status():
    if not is_auth():
        return redirect('/')

    if not is_admin():
        return "Доступ запрещен"

    application_id = request.form['application_id']
    new_status = request.form['id_status']

    execute_query(
        "UPDATE applications SET id_status = %s WHERE id_application = %s",
        (new_status, application_id)
    )

    return redirect('/admin')


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if not is_auth():
        return redirect('/')

    if not is_admin():
        return "Доступ запрещен"

    user_id = request.form['user_id']

    user_data = fetch_one(
        "SELECT id_role FROM users WHERE id_user = %s",
        (user_id,)
    )

    if not user_data:
        return "Пользователь не найден"

    if int(user_id) == session.get('user_id'):
        return "Нельзя удалить самого себя"

    if user_data[0] == 1:
        return "Нельзя удалить администратора"

    execute_query(
        "DELETE FROM users WHERE id_user = %s",
        (user_id,)
    )

    return redirect('/admin')


# -----------------------------
# ВЫХОД
# -----------------------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# -----------------------------
# ЗАПУСК
# -----------------------------

if __name__ == '__main__':
    app.run(debug=True)