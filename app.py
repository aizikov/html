from flask import Flask, render_template, redirect, url_for, flash, request, session
from models import User, Admin, db, Subject

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = '98919753708b5e27a2611fab552e2cce'

# Инициализация SQLAlchemy
db.init_app(app)

# Создание таблиц при запуске приложения
with app.app_context():
    db.create_all()

    # Проверяем, есть ли уже учетная запись администратора
    admin = Admin.query.first()
    if not admin:
        # Создаем учетную запись администратора
        admin = Admin(username='admin', password='h')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', user=user)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        admin = Admin.query.first()
        if admin and admin.check_password(password):
            session['admin'] = True
            return redirect(url_for('users'))
        else:
            flash('Неверный пароль', 'danger')
    return render_template('admin.html')

@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'admin' in session and session['admin']:
        if request.method == 'POST':
            # Обработка изменения роли пользователя
            user_id = request.form['user_id']
            new_role = request.form['new_role']
            user = User.query.get(user_id)
            user.role = new_role
            db.session.commit()
            flash('Роль пользователя обновлена', 'success')
            return redirect(url_for('users'))

        users = User.query.all()
        return render_template('users.html', users=users)
    else:
        return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', user=user)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        subjects = Subject.query.all()
        return render_template('dashboard.html', user=user, subjects=subjects)
    else:
        return redirect(url_for('login'))

@app.route('/add_subject', methods=['POST'])
def add_subject():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'teacher':
            new_subject_name = request.form['new_subject_name']
            subject = Subject(name=new_subject_name)
            db.session.add(subject)
            db.session.commit()
            flash('Дисциплина добавлена', 'success')
    return redirect(url_for('dashboard'))

@app.route('/update_subject/<int:subject_id>', methods=['POST'])
def update_subject(subject_id):
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'teacher':
            subject = Subject.query.get(subject_id)
            new_name = request.form['new_name']
            subject.name = new_name
            db.session.commit()
            flash('Название дисциплины обновлено', 'success')
    return redirect(url_for('dashboard'))

@app.route('/update_study_material/<int:subject_id>', methods=['POST'])
def update_study_material(subject_id):
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'teacher':
            subject = Subject.query.get(subject_id)
            new_study_material = request.form['new_study_material']
            subject.study_material = new_study_material
            db.session.commit()
            flash('Текст для изучения обновлен', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'teacher':
            subject = Subject.query.get(subject_id)
            db.session.delete(subject)
            db.session.commit()
            flash('Дисциплина удалена', 'success')
    return redirect(url_for('dashboard'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'student':
            subjects = Subject.query.all()
            return render_template('student_template.html', user=user, subjects=subjects)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)