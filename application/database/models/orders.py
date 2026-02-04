from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String, Integer, DateTime, Boolean,
    Index, text, Float, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column

from application.database.db import Base


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    posting_number: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    offer_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    commission_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    commission_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    payout: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    customer_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    total_discount_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    total_discount_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    sku: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    last_event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    shipment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    is_finished: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    is_returned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    __table_args__ = (
        Index("ix_order_lines_order", "posting_number"),
    )

