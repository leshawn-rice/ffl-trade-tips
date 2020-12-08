from app.database import db 
from users.models import UserModel

db.drop_all()

db.create_all()

base_user = UserModel(username='admin', password='password', email='admin@ffl-trade-tips.herokuapp.com')

db.session.add(base_user)
db.session.commit()