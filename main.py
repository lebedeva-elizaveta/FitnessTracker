from flasgger import Swagger
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate

from api_routes import api_bp
from models import db

app = Flask(__name__)
swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/sportik_i_tochka'
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(api_bp, url_prefix='/api')


def clear_tables():
    with app.app_context():
        try:
            sql_query = "TRUNCATE TABLE \"user\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"admin\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"activity\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"admin_premium\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"admin_user\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"card\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"user_card\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            sql_query = "TRUNCATE TABLE \"premium\" RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        #clear_tables()

    app.run(debug=True)
