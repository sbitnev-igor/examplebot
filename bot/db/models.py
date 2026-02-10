from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    invited_count: Mapped[int] = mapped_column(Integer, default=0)
    invited_by_hash: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    coins: Mapped[int] = mapped_column(Integer, default=2)
    referral_earnings: Mapped[int] = mapped_column(Integer, default=0)
    referral_percentage: Mapped[int] = mapped_column(Integer, default=5)
    subscription_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.datetime("now", "+3 days"),
    )

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    usage_records: Mapped[list["Usage"]] = relationship(
        "Usage", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, tg_id={self.tg_id}, username={self.username})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount})>"


class Usage(Base):
    __tablename__ = "usage"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    coins_used: Mapped[int] = mapped_column(Integer)
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="usage_records")

    def __repr__(self) -> str:
        return f"<Usage(id={self.id}, user_id={self.user_id}, coins_used={self.coins_used})>"
