from app.models.user import User
from app.extensions import db


class AuthService:
    def authenticate(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.is_active and user.check_password(password):
            return user
        return None

    def create_user(self, username, full_name, password, role="cashier", email=None, employee_id=None):
        if User.query.filter_by(username=username).first():
            raise ValueError(f"Username '{username}' is already taken.")
        user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=role,
            employee_id=employee_id,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        return user

    def change_password(self, user, old_password, new_password):
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect.")
        user.set_password(new_password)
        db.session.commit()
