from decimal import Decimal

from sqlalchemy.orm import Mapped

from app import db


class Product(db.Model):
    __tablename__ = "products"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(100), nullable=False)
    price: Mapped[Decimal] = db.Column(
        db.Numeric(precision=10, scale=2), nullable=False
    )
    description: Mapped[str | None] = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"Product(id={self.id!r}, name={self.name!r}, "
            f"price={self.price!r})"
        )
