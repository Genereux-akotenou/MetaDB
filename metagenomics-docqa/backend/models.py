import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, Boolean, Float, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class UserRole(str, enum.Enum):
    provider = "provider"  # data provider (admin capabilities)
    annotator = "annotator"  # data corrector / reviewer


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.annotator, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chunk_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source_url: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    qa_items = relationship("QAItem", back_populates="chunk")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")


class QAStatus(str, enum.Enum):
    pending = "pending"
    ready = "ready"  # filtered/approved by verifier
    rejected = "rejected"


class QAItem(Base):
    __tablename__ = "qa_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chunk_id_fk: Mapped[int] = mapped_column(ForeignKey("chunks.id"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    category_id_fk: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    status: Mapped[QAStatus] = mapped_column(Enum(QAStatus), default=QAStatus.pending)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunk = relationship("Chunk", back_populates="qa_items")
    category = relationship("Category")
    annotations = relationship("Annotation", back_populates="qa_item")

    __table_args__ = (
        UniqueConstraint("chunk_id_fk", "question", name="uq_chunk_question"),
    )


class Annotation(Base):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    qa_item_id_fk: Mapped[int] = mapped_column(ForeignKey("qa_items.id"))
    edited_question: Mapped[str] = mapped_column(Text)
    edited_answer: Mapped[str] = mapped_column(Text)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    comment: Mapped[str] = mapped_column(Text, default="")
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
    annotated_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    qa_item = relationship("QAItem", back_populates="annotations")


