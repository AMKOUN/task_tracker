import datetime
from flask import Flask, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from markupsafe import escape



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql+psycopg2://sanya:sanya@185.236.25.74:5432/mydb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'task'}
    # TODO: Добавить поля: id (первичный ключ), name (строка), age (целое число)
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    phone_number = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
        }

    tasks = db.relationship('Task', back_populates='users')


class Task(db.Model):
    __tablename__ = 'tasks'
    __table_args__ = {'schema': 'task'}
    # TODO: Добавить поля: id (первичный ключ), name (строка), age (целое число)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('task.users.user_id'))
    users = db.relationship('User', back_populates='tasks')

    def __repr__(self):
        return f"<Task(id={self.id}, status='{self.status}', description='{self.description}', title='{self.title}', description={self.description})>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "done": self.done,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user_id": self.user_id,
        }

@app.route('/create_task', methods=['POST'])
def create_task():

    # Получаем JSON-данные из тела запроса
    data = request.get_json()

    # Если данных нет — возвращаем ошибку 400 (Bad Request)
    if not data:
        return jsonify({"error": "Не переданы данные"}), 400
    print(data)

    # Проверяем наличие обязательных полей
    if 'done' not in data or 'status' not in data or 'title' not in data:
        return jsonify({"error": "Поля обязательны"}), 400

    # Создаём нового пользователя из полученных данных
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),  # используем .get() — не будет ошибки, если "age" не передан
        status=data.get('status'),
        done=data.get('done'),
        user_id=data.get('user_id'),
    )

    try:
        # Добавляем пользователя в сессию (подготовка к вставке)
        db.session.add(new_task)
        # Сохраняем изменения в базе данных
        db.session.commit()

        # Возвращаем успешный ответ с данными добавленного пользователя
        return jsonify({
            "message": "Пользователь добавлен",
            "user": new_task.to_dict()
        }), 201

    except Exception as e:
        # Если произошла ошибка — откатываем транзакцию
        db.session.rollback()
        # Возвращаем ошибку 500 (внутренняя ошибка сервера)
        return jsonify({"error": str(e)}), 500



@app.route('/users', methods=['POST'])
def add_user():
    """Добавление нового пользователя через POST-запрос с JSON"""

    # Получаем JSON-данные из тела запроса
    data = request.get_json()

    # Если данных нет — возвращаем ошибку 400 (Bad Request)
    if not data:
        return jsonify({"error": "Не переданы данные"}), 400
    print(data)

    # Проверяем наличие обязательных полей
    if 'phone_number' not in data or 'user_id' not in data:
        return jsonify({"error": "Поля 'phone_number' и 'user_id' обязательны"}), 400

    # Создаём нового пользователя из полученных данных
    new_user = User(
        user_id=data['user_id'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),  # используем .get() — не будет ошибки, если "age" не передан
        phone_number=data['phone_number'],
    )

    try:
        # Добавляем пользователя в сессию (подготовка к вставке)
        db.session.add(new_user)
        # Сохраняем изменения в базе данных
        db.session.commit()

        # Возвращаем успешный ответ с данными добавленного пользователя
        return jsonify({
            "message": "Пользователь добавлен",
            "user": new_user.to_dict()
        }), 201

    except Exception as e:
        # Если произошла ошибка — откатываем транзакцию
        db.session.rollback()
        # Возвращаем ошибку 500 (внутренняя ошибка сервера)
        return jsonify({"error": str(e)}), 500


@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks_by_user(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@app.route('/get_task/<int:task_id>', methods=['GET'])
def get_task(task_id):

    # Проверяем, что задача принадлежит пользователю
    task = Task.query.filter_by(id=task_id).first()
    if not task:
        return jsonify({"error": "Такой задачи не существует, ты еблан"}), 403

    return jsonify({
        "task": task.to_dict()
    })


@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    data = request.get_json()

    # user_id is required to avoid deleting someone else's task
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id обязателен"}), 400

    # Check if the task exists and belongs to the user
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Эта задача не принадлежит пользователю"}), 403

    try:
        db.session.delete(task)
        db.session.commit()

        return jsonify({
            "message": "Задача удалена",
            "task_id": task_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@app.route('/get_task/<task_title>', methods=['GET'])
def get_task_by_title(task_title):

    # Проверяем, что задача принадлежит пользователю
    task = Task.query.filter_by(title=task_title).first()
    if not task:
        return jsonify({"error": "Такой задачи не существует, ты еблан"}), 403

    return jsonify({
        "task": task.to_dict()
    })


@app.route('/update_task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()

    # Проверяем, передан ли user_id
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id обязателен"}), 400

    # Проверяем, что задача принадлежит пользователю
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Эта задача не принадлежит пользователю"}), 403

    # Обновляем данные
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        task.status = data["status"]
    if "done" in data:
        task.done = data["done"]

    db.session.commit()

    return jsonify({
        "message": "Задача обновлена",
        "task": task.to_dict()
    })



with app.app_context():
    # Создаёт все таблицы, если их ещё нет в базе данных
    db.create_all()

if __name__ == '__main__':
    # Запускаем Flask-сервер в режиме отладки
    # (при изменении кода сервер перезапускается автоматически)
    app.run(debug=True)