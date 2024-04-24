import sqlite3
import os
from flask import Flask, g


DATABASE = 'tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'asfnhj23h541254kjksd'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def regestration(self, name, username, password):
        try:
            self.__cur.execute(f"SELECT COUNT(*) as count FROM users WHERE username = '{username}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким никнеймом уже существует")
                return False

            self.__cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, FALSE)", (name, username, password))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления данных в БД" + str(e))
            return False

        return True

    def add_lesson(self, lesson_topic, user_id, terms, translations, examples):
        try:
            self.__cur.execute("INSERT INTO lessons (lesson_topic, user_id) VALUES (?, ?)", (lesson_topic, user_id))
            lesson_id = self.__cur.lastrowid  # Получаем ID нового урока

            # Для каждого термина, перевода и примера использования вставляем запись в таблицу terms
            for term, translation, example in zip(terms, translations, examples):
                self.__cur.execute("INSERT INTO terms (lesson_id, term, translation, example) VALUES (?, ?, ?, ?)",
                                   (lesson_id, term, translation, example))

            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления данных в БД" + str(e))
            return False

        return True

    def get_user(self, get_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = '{get_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print('Ошибка получения данных из БД' + str(e))

        return False

    def get_user_by_username(self, username):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE username = '{username}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print('Ошибка получения данных из БД' + str(e))

        return False

    def get_users(self):
        try:
            self.__cur.execute("SELECT * FROM users WHERE admin = 0")
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print('Ошибка получения данных из БД' + str(e))

        return False

    def get_lessons(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM lessons WHERE user_id = ?", (user_id,))
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: " + str(e))

        return False

    def get_lesson(self, lesson_id):
        try:
            self.__cur.execute("SELECT term, translation, example FROM terms WHERE lesson_id = ?", (lesson_id,))
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: " + str(e))

        return False

    def del_lesson(self, lesson_id):
        try:
            self.__cur.execute("DELETE FROM terms WHERE lesson_id = ?", (lesson_id,))
            self.__cur.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка удаления данных из БД: " + str(e))

        return False

    def upgrade_lesson(self, lesson_id, terms, translations, examples):
        try:
            # Удаляем все записи связанные с lesson_id из таблицы terms
            self.__cur.execute("DELETE FROM terms WHERE lesson_id = ?", (lesson_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления данных из БД: " + str(e))
            return False

        try:
            # Вставляем новые записи с новыми данными
            for term, translation, example in zip(terms, translations, examples):
                self.__cur.execute("INSERT INTO terms (lesson_id, term, translation, example) VALUES (?, ?, ?, ?)",
                                   (lesson_id, term, translation, example))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления данных в БД: " + str(e))
            return False

        return True

    def user_by_les_id(self, lesson_id):
        try:
            self.__cur.execute("SELECT user_id FROM lessons WHERE id = ?", (lesson_id,))
            return self.__cur.fetchone()
        except sqlite3.Error as e:
            print("Ошибка удаления данных из БД: " + str(e))
        return False

    def get_lesson_name(self, lesson_id):
        try:
            self.__cur.execute("SELECT lesson_topic FROM lessons WHERE id = ?", (lesson_id,))
            return self.__cur.fetchone()
        except sqlite3.Error as e:
            print("Ошибка удаления данных из БД: " + str(e))
        return False


    def feed_back(self, u_name, lesson_name, message):
        try:
            self.__cur.execute("INSERT INTO feedback (u_name, lesson_name, message) VALUES (?, ?, ?)", (u_name, lesson_name, message,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления данных в БД: " + str(e))
            return False

        return True

    def get_feedback(self):
        try:
            self.__cur.execute("SELECT * FROM feedback")
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print('Ошибка получения данных из БД' + str(e))

        return False

    def feedback_del(self, message):
        try:
            self.__cur.execute("DELETE FROM feedback WHERE message = ?", (message,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка удаления данных из БД: " + str(e))
            return False

        return True

    def add_post(self, post_topic, post_summery, post_oppic, post_conts, post_pics):
        try:
            self.__cur.execute("INSERT INTO posts (post_topic, post_summery, post_oppic) VALUES (?, ?, ?)", (post_topic, post_summery, post_oppic,))
            post_id = self.__cur.lastrowid  # Получаем ID нового урока

            # Для каждого термина, перевода и примера использования вставляем запись в таблицу terms
            for post_cont, post_pic in zip(post_conts, post_pics):
                self.__cur.execute("INSERT INTO contpost (post_cont, post_pic, post_id) VALUES (?, ?, ?)",
                                   (post_cont, post_pic, post_id))

            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления данных в БД" + str(e))
            return False

        return True

    def get_posts(self):
        try:
            self.__cur.execute("SELECT * FROM posts")
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: " + str(e))

        return False

    def get_post(self, post_id):
        try:
            self.__cur.execute("SELECT * FROM contpost WHERE post_id = ?", (post_id,))
            return self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: " + str(e))

        return False

@app.teardown_appcontext
def close_db():
    if hasattr(g, 'link_db'):
        g.link_db.close()
