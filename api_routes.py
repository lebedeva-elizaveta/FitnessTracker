from datetime import datetime, timedelta

from flask import jsonify, request
from jwt import decode
from models import db, User, Admin, Activity, Premium, Admin_User, Admin_Premium
from config import SECRET_KEY
import jwt
from utils import check_email, generate_password_hash, check_password, is_premium, check_access_token
from flask import Blueprint

api_bp = Blueprint('api', __name__)


@api_bp.route('/register_user', methods=['POST'])
def register_user():
    """
    Регистрация пользователя
    ---
    tags:
      - Пользователи
    summary: Создать новый аккаунт
    parameters:
      - name: email
        in: header
        required: true
        type: string
        description: Email пользователя
      - name: register_data
        in: body
        required: true
        schema:
          id: RegisterRequest
          required:
            - name
            - weight
            - image
            - phone
            - birthday
            - password
          properties:
            name:
              type: string
              description: Имя пользователя
            weight:
              type: integer
              description: Вес пользователя
            image:
              type: string
              description: Аватар пользователя
            phone:
              type: string
              description: Телефон пользователя
            birthday:
              type: string
              description: Дата рождения пользователя в формате "гггг-мм-дд"
            password:
              type: string
              description: Пароль пользователя
    responses:
      201:
        description: Успешная регистрация
        schema:
          id: RegisterResponse
          properties:
            success:
              type: boolean
              description: Результат регистрации
            access_token:
              type: string
              description: Токен доступа пользователя
            user_id:
              type: integer
              description: ID пользователя
      409:
        description: Ошибка, если email уже используется
        schema:
          id: EmailIsUnavailable
          properties:
            free:
              type: boolean
              description: Проверка доступности email
    """

    email = request.headers.get('email')
    register_data = request.json

    email_is_free = check_email(email)
    if not email_is_free:
        return jsonify({"free": False}), 409

    new_user = User(
        name=register_data['name'],
        weight=register_data['weight'],
        avatar=register_data['image'],
        phone=register_data['phone'],
        birthday=register_data['birthday'],
        email=email,
        password_hash=generate_password_hash(register_data['password'])
    )
    db.session.add(new_user)
    db.session.commit()

    access_token = jwt.encode(payload={'sub': new_user.id}, key=SECRET_KEY, algorithm='HS256')

    return jsonify({
        "success": True,
        "access_token": access_token,
        "user_id": new_user.id
    }), 201


@api_bp.route('/register_admin', methods=['POST'])
def register_admin():
    """
    Регистрация администратора
    ---
    tags:
      - Администраторы
    summary: Создать новый аккаунт администратора
    parameters:
      - name: email
        in: header
        required: true
        type: string
        description: Email администратора
      - name: register_data
        in: body
        required: true
        schema:
          id: RegisterAdminRequest
          required:
            - name
            - image
            - phone
            - birthday
            - password
          properties:
            name:
              type: string
              description: Имя администратора
            image:
              type: string
              description: Аватар администратора
            phone:
              type: string
              description: Телефон администратора
            birthday:
              type: string
              description: Дата рождения администратора в формате "гггг-мм-дд"
            password:
              type: string
              description: Пароль администратора
    responses:
      201:
        description: Успешная регистрация
        schema:
          id: RegisterAdminResponse
          properties:
            success:
              type: boolean
              description: Результат регистрации
            access_token:
              type: string
              description: Токен доступа администратора
            admin_id:
              type: integer
              description: ID администратора
      409:
        description: Ошибка, если email уже используется
        schema:
          id: EmailIsUnavailable
          properties:
            free:
              type: boolean
              description: Проверка доступности email
    """

    email = request.headers.get('email')
    register_data = request.json

    email_is_free = check_email(email)
    if not email_is_free:
        return jsonify({"free": False}), 409

    new_admin = Admin(
        name=register_data['name'],
        avatar=register_data['image'],
        phone=register_data['phone'],
        birthday=register_data['birthday'],
        email=email,
        password_hash=generate_password_hash(register_data['password'])
    )
    db.session.add(new_admin)
    db.session.commit()

    access_token = jwt.encode(payload={'sub': new_admin.id}, key=SECRET_KEY, algorithm='HS256')

    return jsonify({
        "success": True,
        "access_token": access_token,
        "admin_id": new_admin.id
    }), 201


@api_bp.route('/login', methods=['POST'])
def login():
    """
    Вход пользователя
    ---
    tags:
      - Пользователи
    summary: Войти в аккаунт
    parameters:
      - name: login_data
        in: body
        required: true
        schema:
          id: LoginRequest
          properties:
            email:
              type: string
              description: Email пользователя
            password:
              type: string
              description: Пароль пользователя
    responses:
      200:
        description: Успешный вход
        schema:
          id: LoginResponse
          properties:
            success:
              type: boolean
              description: Результат входа
            access_token:
              type: string
              description: Токен доступа пользователя
            user_id:
              type: integer
              description: ID пользователя
            role:
              type: string
              description: Роль пользователя
      401:
        description: Неправильный пароль
        schema:
          id: IncorrectPasswordResponse
          properties:
            success:
              type: boolean
              description: Результат входа
            error:
              type: string
              description: Ошибка
      403:
        description: Пользователь заблокирован
        schema:
          id: UserIsBlockedResponse
          properties:
            success:
              type: boolean
              description: Результат входа
            error:
              type: string
              description: Ошибка
      404:
        description: Пользователь не найден
        schema:
          id: UserNotFoundResponse
          properties:
            success:
              type: boolean
              description: Результат входа
            error:
              type: string
              description: Ошибка
    """
    login_data = request.json
    email = login_data.get('email')
    password = login_data.get('password')
    # ищем какая роль
    admin = Admin.query.filter_by(email=email).first()
    if admin:
        if not check_password(admin.password_hash, password):
            return jsonify({"success": False, "error": "INCORRECT_PASSWORD"}), 401
        return jsonify({
            "success": True,
            "access_token": jwt.encode(payload={'sub': admin.id}, key=SECRET_KEY, algorithm='HS256'),
            "admin_id": admin.id,
            "role": "admin"
        }), 200

    user = User.query.filter_by(email=email).first()
    if user:
        if user.is_blocked:
            return jsonify({"success": False, "error": "USER_BLOCKED"}), 403
        if not check_password(user.password_hash, password):
            return jsonify({"success": False, "error": "INCORRECT_PASSWORD"}), 401
        if is_premium(user.id):
            role = "premium"
        else:
            role = "regular"
        return jsonify({
            "success": True,
            "access_token": jwt.encode(payload={'sub': user.id}, key=SECRET_KEY, algorithm='HS256'),
            "user_id": user.id,
            "role": role
        }), 200

    return jsonify({"success": False, "error": "USER_NOT_FOUND"}), 404


@api_bp.route('/add_activity', methods=['POST'])
def add_activity():
    """
    Добавление активности
    ---
    tags:
      - Активности
    summary: Добавить активность
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Токен доступа пользователя
      - name: activity_data
        in: body
        required: true
        schema:
          id: AddActivityRequest
          required:
            - activity_type
            - date
            - image
            - avg_speed
            - distance_in_meters
            - timestamp
            - calories_burned
          properties:
            activity_type:
              type: string
              description: Тип активности
            date:
              type: string
              description: Дата активности
            image:
              type: string
              description: Отображение пути на карте
            avg_speed:
              type: number
              format: float
              description: Средняя скорость
            distance_in_meters:
              type: integer
              description: Расстояние в метрах
            duration:
              type: integer
              description: Длительность активности в секундах
            calories_burned:
              type: integer
              description: Сожженные калории
    responses:
      201:
        description: Успешное добавление активности
        schema:
          id: AddActivityResponse
          properties:
            success:
              type: boolean
              description: Результат добавления активности
            activity_id:
              type: integer
              description: ID активности
      401:
        description: Токен некорректный
        schema:
          id: TokenErrorResponse
          properties:
            success:
              type: boolean
              description: Результат добавления активности
      404:
        description: Ошибка, если пользователь не найден
        schema:
          id: UserNotFoundResponse
          properties:
            free:
              type: boolean
              description: Результат добавления активности
    """
    access_token = request.headers.get('Authorization')
    activity_data = request.json
    access_token_is_correct = check_access_token(access_token)
    if not access_token_is_correct:
        return jsonify({"success": False}), 401

    clear_token = access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    user = User.query.filter_by(id=payload['sub']).first()
    if not user:
        return jsonify({"success": False}), 404
    new_activity = Activity(
        user_id=user.id,
        duration=activity_data['duration'],
        distance=activity_data['distance_in_meters'],
        calories=activity_data['calories_burned'],
        speed=activity_data['avg_speed'],
        date=activity_data['date'],
        image=activity_data['image'],
        type=activity_data['activity_type']
    )

    db.session.add(new_activity)
    db.session.commit()

    return jsonify({
        "success": True,
        "activity_id": new_activity.id
    }), 201


@api_bp.route('/get_activities', methods=['GET'])
def get_activities():
    """
    Получение списка активностей пользователя
    ---
    tags:
      - Активности
    summary: Получить список активностей
    description: Возвращает список всех активностей пользователя.
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Токен доступа пользователя
    responses:
      201:
        description: Успешный запрос
        schema:
          id: ActivityResponse
          properties:
            success:
              type: boolean
              description: Результат добавления активности
            activities:
              type: array
              items:
                $ref: '#/definitions/ActivityResponse'
          examples:
          NoActivities:
            description: Нет активностей
            value:
              success: true
              message: No activities yet
      401:
        description: Токен некорректный
        schema:
          id: TokenErrorResponse
          properties:
            success:
              type: boolean
              description: Результат отображения активностей
      404:
        description: Ошибка, если пользователь не найден
        schema:
          id: UserNotFoundResponse
          properties:
            free:
              type: boolean
              description: Результат отображения активностей
    definitions:
      ActivityResponse:
        type: object
        required:
          - id
          - activity_type
          - image
          - date
          - avg_speed
          - distance_in_meters
          - duration
          - calories_burned
        properties:
          id:
            type: integer
            description: ID активности
          activity_type:
            type: string
            description: Тип активности (running, cycling, swimming)
          image:
            type: string
            description: Отображение пути на карте
          date:
            type: string
            format: date
            description: Дата активности в формате "гггг-мм-дд"
          avg_speed:
            type: number
            description: Средняя скорость
          distance_in_meters:
            type: integer
            description: Расстояние в метрах
          duration:
            type: integer
            description: Продолжительность в секундах
          calories_burned:
            type: integer
            description: Сожженные калории
    """
    access_token = request.headers.get('Authorization')
    access_token_is_correct = check_access_token(access_token)
    if not access_token_is_correct:
        return jsonify({"success": False}), 401
    clear_token = access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    user = User.query.filter_by(id=payload['sub']).first()
    if not user:
        return jsonify({"success": False}), 404
    user_id = payload['sub']
    user_activities = Activity.query.filter_by(user_id=user_id).all()
    if not user_activities:
        return jsonify({"success": True, "message": "No activities yet"}), 200
    list_of_activities = []
    for activity in user_activities:
        activity_data = {
            "id": activity.id,
            "activity_type": activity.type,
            "image": activity.image,
            "date": activity.date.strftime('%Y-%m-%d'),
            "avg_speed": activity.speed,
            "distance_in_meters": activity.distance,
            "duration": activity.duration,
            "calories_burned": activity.calories
        }
        list_of_activities.append(activity_data)
    return jsonify({"success": True, "activities": list_of_activities}), 200


@api_bp.route('/admin_actions', methods=['PUT'])
def admin_actions_put():
    """
    Действия администратора
    ---
    tags:
      - Администраторы
    summary: Действия администраторов с пользователями
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Токен доступа администратора
      - name: request_data
        in: body
        required: true
        schema:
          id: AdminActionRequest
          properties:
            user_id:
              type: integer
              description: ID пользователя
            action:
              type: string
              enum: [block, unblock, revoke_premium]
              description: Выбранное действие
    responses:
      200:
        description: Успешное действие
        schema:
          id: AdminActionResponse
          properties:
            success:
              type: boolean
              description: Результат действия
            action:
              type: string
              description: Выполненное действие
      400:
        description: Некорректное действие
        schema:
          id: InvalidActionErrorResponse
          properties:
            success:
              type: boolean
              description: Результат действия
            message:
              type: string
              description: Сообщение о некорректном действии
      401:
        description: Токен некорректный
        schema:
          id: TokenErrorResponse
          properties:
            success:
              type: boolean
              description: Результат действия
      404:
        description: Пользователь или админ не найдены
        schema:
          id: NotFoundErrorResponse
          properties:
            success:
              type: boolean
              description: Результат действия
            message:
              type: string
              description: Сообщение о том кто не найден
    """
    access_token = request.headers.get('Authorization')
    access_token_is_correct = check_access_token(access_token)
    if not access_token_is_correct:
        return jsonify({"success": False}), 401
    clear_token = access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    admin = Admin.query.filter_by(id=payload['sub']).first()
    admin_id = payload['sub']
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    request_data = request.json
    user_id = request_data['user_id']
    action = request_data['action']
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if action == "block":
        user.is_blocked = True
        add_admin_user_data(admin_id, user_id, action)
        db.session.commit()
        return jsonify({"success": True, "action": "block"})
    elif action == "unblock":
        user.is_blocked = False
        add_admin_user_data(admin_id, user_id, action)
        db.session.commit()
        return jsonify({"success": True, "action": "unblock"})
    elif action == "revoke_premium":
        premium = Premium.query.filter(
            Premium.user_id == user_id,
            Premium.start_date <= datetime.utcnow(),
            Premium.end_date >= datetime.utcnow()
        ).order_by(
            Premium.start_date.desc(), Premium.end_date.desc()
        ).first()
        premium.end_date = datetime.utcnow()
        add_admin_premium_data(admin_id, premium.id, action)
        db.session.commit()
        return jsonify({"success": True, "action": "revoke_premium"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400


@api_bp.route('/admin_actions', methods=['POST'])
def admin_actions_post():
    """
    Действия администратора
    ---
    tags:
      - Администраторы
    summary: Действия администраторов с пользователями
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Токен доступа администратора
      - name: request_data
        in: body
        required: true
        schema:
          id: AdminActionRequest
          properties:
            user_id:
              type: integer
              description: ID пользователя
            action:
              type: string
              enum: [grant_premium]
              description: Только для выдачи премиума
    responses:
      200:
        description: Успешное действие
        schema:
          id: AdminActionResponse
          properties:
            success:
              type: boolean
              description: Результат действия
            action:
              type: string
              description: Выполненное действие
      400:
        description: Некорректное действие
        schema:
          id: InvalidActionErrorResponse
          properties:
            success:
              type: boolean
              description: Результат действия
            message:
              type: string
              description: Сообщение о некорректном действии
      401:
        description: Токен некорректный
        schema:
          id: TokenErrorResponse
          properties:
            success:
              type: boolean
              description: Результат действия
      404:
        description: Пользователь или админ не найдены
        schema:
          id: NotFoundErrorResponse
          properties:
            success:
              type: boolean
              description: Результат действия
            message:
              type: string
              description: Сообщение о том кто не найден
    """
    access_token = request.headers.get('Authorization')
    access_token_is_correct = check_access_token(access_token)
    if not access_token_is_correct:
        return jsonify({"success": False}), 401
    clear_token = access_token.replace('Bearer ', '')
    payload = decode(jwt=clear_token, key=SECRET_KEY, algorithms=['HS256', 'RS256'])
    admin = Admin.query.filter_by(id=payload['sub']).first()
    admin_id = payload['sub']
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    request_data = request.json
    user_id = request_data['user_id']
    action = request_data['action']
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    if action == "grant_premium":
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)
        new_premium = Premium(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(new_premium)
        db.session.commit()
        add_admin_premium_data(admin_id, new_premium.id, action)
        return jsonify({"success": True, "action": "grant_premium"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400


@api_bp.route('/add_admin_user_data', methods=['POST'])
def add_admin_user_data(admin_id, user_id, action):

    admin = Admin.query.get(admin_id)
    user = User.query.get(user_id)
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    admin_user_data = Admin_User(admin_id=admin_id, user_id=user_id, action=action)
    db.session.add(admin_user_data)
    db.session.commit()

    return jsonify({"success": True}), 201


@api_bp.route('/add_admin_premium_data', methods=['POST'])
def add_admin_premium_data(admin_id, premium_id, action):

    admin = Admin.query.get(admin_id)
    premium = Premium.query.get(premium_id)
    if not admin:
        return jsonify({"success": False, "message": "Admin not found"}), 404
    if not premium:
        return jsonify({"success": False, "message": "Premium not found"}), 404
    admin_premium_data = Admin_Premium(admin_id=admin_id, premium_id=premium_id, action=action)
    db.session.add(admin_premium_data)
    db.session.commit()

    return jsonify({"success": True}), 201
