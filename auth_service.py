from database.connection import SessionLocal
from database.models import User
from utils.password_hash import verify_password
from utils.jwt_helper import create_token

class AuthService:

    @staticmethod
    def login(username, password):
        session = SessionLocal()
        user = session.query(User).filter_by(username=username).first()

        if not user:
            return {"error": "Invalid username"}

        if not verify_password(password, user.password_hash):
            return {"error": "Invalid password"}

        token = create_token(user.user_id, user.role.role_name)
        return {"token": token}
