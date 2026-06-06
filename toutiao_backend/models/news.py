from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )


class NewsCategory(Base):
    __tablename__ = "news_category"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="分类ID"
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="分类名称"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="排序顺序"
    )

    news_list: Mapped[List["News"]] = relationship(
        back_populates="category"
    )


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="新闻ID"
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="新闻标题"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="新闻简介"
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="新闻内容"
    )
    image: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="封面图片URL"
    )
    author: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="作者"
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "news_category.id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False,
        comment="分类ID"
    )
    views: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="浏览量"
    )
    publish_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="发布时间"
    )

    category: Mapped["NewsCategory"] = relationship(
        back_populates="news_list"
    )

    related_items: Mapped[List["RelatedNews"]] = relationship(
        foreign_keys="RelatedNews.news_id",
        back_populates="news",
        cascade="all, delete-orphan"
    )

    related_by_items: Mapped[List["RelatedNews"]] = relationship(
        foreign_keys="RelatedNews.related_news_id",
        back_populates="related_news",
        cascade="all, delete-orphan"
    )


class RelatedNews(Base):
    __tablename__ = "related_news"

    __table_args__ = (
        UniqueConstraint(
            "news_id",
            "related_news_id",
            name="news_related_unique"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="关联ID"
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="新闻ID"
    )
    related_news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="相关新闻ID"
    )

    news: Mapped["News"] = relationship(
        foreign_keys=[news_id],
        back_populates="related_items"
    )

    related_news: Mapped["News"] = relationship(
        foreign_keys=[related_news_id],
        back_populates="related_by_items"
    )
