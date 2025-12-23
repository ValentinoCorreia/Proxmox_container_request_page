from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String as AlchemyString, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from models.connection import db

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    # email: Mapped[str] = mapped_column(AlchemyString(254), nullable=True)
    username: Mapped[str] = mapped_column(AlchemyString(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    containers: Mapped[list["Container"]] = relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_check(self, password) -> bool:
        if (self.password_hash == None):
            return False
        else:
            return check_password_hash(self.password_hash, password)