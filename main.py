from flask import Flask, render_template, url_for, request, session, redirect, abort, flash
from db import get_db, FDataBase, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from userLogin import UserLogin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = 'asfnhj23h541254kjksd'

login_manager = LoginManager(app)

menu = [{"name": "Главная", "url": "index"},
        {"name": "Аккаунт", "url": "login"}]


dbase = None

UPLOAD_FOLDER = 'static/pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


@app.route("/")
def index():
    posts = dbase.get_posts()
    return render_template('index.html', posts=posts, menu=menu)



@app.route("/logout")
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route("/profile")
@login_required
def profile():
    if current_user.get_role() == 1:
        users = dbase.get_users()
        return render_template('profile.html', title="Профиль администратора", users=users, menu=menu)
    else:
        username = current_user.get_username()
        user_info = dbase.get_user_by_username(username)
        return render_template('user_profile.html', title="Ваш профиль", user_info=user_info, menu=menu)


@app.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    if current_user.get_role() != 1:
        abort(403)
    user_info = dbase.get_user(user_id)
    if user_info:
        return render_template('user_profile.html', title=f"{user_info['name']}", user_info=user_info, menu=menu)
    else:
        # Обработка случая, если пользователь не найден
        abort(404)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        user = dbase.get_user_by_username(request.form['username'])
        if user and check_password_hash(user['password'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('rmember') else False
            login_user(userlogin, remember=rm)
            return redirect(url_for('profile'))

        flash("Неверно указан логин или пароль", "error")

    return render_template("login.html", menu=menu, title="Авторизация")


@app.route("/regestration", methods=["POST", "GET"])
def regestration():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['username']) > 4 and len(request.form['password']) > 4 and request.form['password'] == request.form['password2']:
            hash = generate_password_hash(request.form['password'])
            res = dbase.regestration(request.form['name'], request.form['username'], hash)
            if not res:
                flash('Ошибка регистрации', category='error')
            else:
                flash('Успешная регистрация', category='success')
                return redirect(url_for('login'))
        else:
            flash('Неверно указаны данные', category='error')
    return render_template('regestration.html', menu=menu, title='Регистрация')


@app.route("/add_lesson/<int:user_id>", methods=["POST", "GET"])
@login_required
def add_lesson(user_id):
    if current_user.get_role() != 1:
        abort(403)
    if request.method == 'POST':
        lesson_topic = request.form.get('lesson_topic')
        terms = request.form.getlist('term')
        translations = request.form.getlist('translation')
        examples = request.form.getlist('example')

        if not all(terms) or not all(translations) or not all(examples):
            return redirect(url_for('add_lesson', user_id=user_id))
        else:
            res = dbase.add_lesson(lesson_topic, user_id, terms, translations, examples)
            if not res:
                flash('Ошибка добавления урока', category='error')
            else:
                flash('Урок успешно добавлен', category='success')
                return redirect(url_for('lessons', user_id=user_id))

    return render_template("add_lesson.html", title="Добавить урок", menu=menu)


@app.route("/lessons/<int:user_id>")
@login_required
def lessons(user_id):
    lessons = dbase.get_lessons(user_id)
    user_id = user_id

    return render_template('lessons.html', title="Задания", lessons=lessons, user_id=user_id, menu=menu)


@app.route("/lesson/<int:lesson_id>", methods=["POST", "GET"])
@login_required
def lesson(lesson_id):
    lesson_data = dbase.get_lesson(lesson_id)
    user_id = dbase.user_by_les_id(lesson_id)
    if request.method == 'POST':
        lesson_n = dbase.get_lesson_name(lesson_id)
        lesson_name = lesson_n['lesson_topic']
        u_name = current_user.get_name()
        message = request.form.get('message')
        res = dbase.feed_back(u_name, lesson_name, message)
        if not res:
            flash('Ошибка отправления сообщения', category='error')
        else:
            flash('Сообщение успешно отправленно', category='success')
            return redirect(url_for('lessons', user_id=user_id['user_id']))

    return render_template('lesson.html', lesson_data=lesson_data, user_id=user_id, menu=menu)


@app.route("/lesson_delite/<int:lesson_id>")
@login_required
def lesson_delite(lesson_id):
    user_id = dbase.user_by_les_id(lesson_id)
    dbase.del_lesson(lesson_id)
    return redirect(url_for('lessons', user_id=user_id['user_id']))


@app.route("/lesson_change/<int:lesson_id>", methods=["POST", "GET"])
@login_required
def lesson_change(lesson_id):
    changed_lesson = dbase.get_lesson(lesson_id)
    if current_user.get_role() != 1:
        abort(403)
    if request.method == 'POST':
        terms = request.form.getlist('term')
        translations = request.form.getlist('translation')
        examples = request.form.getlist('example')

        if not all(terms) or not all(translations) or not all(examples):
            return redirect(url_for('profile'))
        else:
            res = dbase.upgrade_lesson(lesson_id, terms, translations, examples)
            if not res:
                flash('Ошибка изменения урока', category='error')
            else:
                flash('Урок успешно изменён', category='success')
                user_id = dbase.user_by_les_id(lesson_id)
                return redirect(url_for('lessons', user_id=user_id['user_id']))

    return render_template('lesson_change.html', changed_lesson=changed_lesson, menu=menu)


@app.route("/feedback")
@login_required
def feedback():
    if current_user.get_role() == 1:
        fback = dbase.get_feedback()
        return render_template('feedback.html', fback=fback, title="Вопросы пользователей", menu=menu)
    else:
        abort(403)


@app.route("/del_feedback/<string:message>")
@login_required
def del_feedback(message):
    dbase.feedback_del(message)
    fback = dbase.get_feedback()

    return render_template('feedback.html', fback=fback, title="Вопросы пользователей", menu=menu)


@app.route("/add_post", methods=["POST", "GET"])
@login_required
def add_post():
    if current_user.get_role() != 1:
        abort(403)
    if request.method == 'POST':
        post_topic = request.form.get('article_title')
        post_summery = request.form.get('article_description')
        post_oppic_file = request.files['article_image']
        post_oppic = post_oppic_file.filename
        post_oppic_file.save(os.path.join(app.config['UPLOAD_FOLDER'], post_oppic))
        post_conts = request.form.getlist('additional_content')
        post_pics_files = request.files.getlist('additional_images')
        post_pics = [pic.filename for pic in post_pics_files]
        for file in post_pics_files:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        res = dbase.add_post(post_topic, post_summery, post_oppic, post_conts, post_pics)
        if not res:
            flash('Ошибка добавления урока', category='error')
        else:
            flash('Урок успешно добавлен', category='success')
            return redirect(url_for('index'))

    return render_template("add_post.html", title="Добавить статью", menu=menu)


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
@login_required
def post(post_id):
    post_cont = dbase.get_post(post_id)
    return render_template('post.html', post_cont=post_cont, menu=menu)



@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404


@app.errorhandler(403)
def page_not_found(error):
    return render_template('page403.html', title="У вас недостаточно прав", menu=menu), 403


if __name__ == "__main__":
    app.run(debug=True)
