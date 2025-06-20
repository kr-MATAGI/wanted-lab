from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    ARRAY,
    DateTime,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.utils.database import Base

class CompanyID(Base):
    """회사 ID"""
    __tablename__ = "tbl_company_ids"

    id = Column(Integer, primary_key=True, autoincrement=True)
    add_date = Column(DateTime, nullable=False, default=func.now())


class Language(Base):
    """사용하는 언어 정보"""
    __tablename__ = "tbl_languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    language_type = Column(Text, nullable=False)
    add_date = Column(DateTime, nullable=False, default=func.now())


class CompanyName(Base):
    """회사 정보 모델"""
    __tablename__ = "tbl_company_names"
    __table_args__ = (
        UniqueConstraint('name', 'rel_id', name='tbl_company_names_name_rel_id_unique'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    company_id = Column(
        Integer,
        ForeignKey("tbl_company_ids.id"),
        nullable=False,
    )
    rel_id = Column(
        Integer,
        ForeignKey("tbl_company_name_relations.id"),
        nullable=False,
    )
    language_id = Column(
        Integer,
        ForeignKey("tbl_languages.id"),
        nullable=False,
    )
    add_date = Column(DateTime, nullable=False, default=func.now())
    
    # 관계 설정
    company = relationship("CompanyID", backref="company_names")
    language = relationship("Language", backref="company_names")
    company_name_relation = relationship("CompanyNameRelation", backref="company_names")


class CompanyNameRelation(Base):
    """회사 이름 의미 관계 모델"""
    __tablename__ = "tbl_company_name_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        Integer,
        ForeignKey("tbl_company_ids.id"),
        nullable=False,
    )
    name_ids = Column(MutableList.as_mutable(ARRAY(Integer)), nullable=False)
    add_date = Column(DateTime, nullable=False, default=func.now())
    
    # 관계 설정
    company = relationship("CompanyID", backref="company_name_relations")


class Tag(Base):
    """태그 정보 모델"""
    __tablename__ = "tbl_tags"
    __table_args__ = (
        UniqueConstraint('tag_name', 'rel_id', name='tbl_tags_tag_name_rel_id_unique'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(Text, nullable=False)
    rel_id = Column(
        Integer,
        ForeignKey("tbl_tag_relations.id"),
        nullable=False,
    )
    company_id = Column(
        Integer, 
        ForeignKey("tbl_company_ids.id"),
        nullable=False,
    )
    language_id = Column(
        Integer, 
        ForeignKey("tbl_languages.id"),
    )
    add_date = Column(DateTime, nullable=False, default=func.now())

    # 관계 설정
    company = relationship("CompanyID", backref="tags")
    language = relationship("Language", backref="tags")
    tag_relation = relationship("TagRelation", backref="tags")


class TagRelation(Base):
    """ 공통 태그 의미 관계 모델"""
    __tablename__ = "tbl_tag_relations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(
        Integer,
        ForeignKey("tbl_company_ids.id"),
        nullable=False
    )
    tag_ids = Column(MutableList.as_mutable(ARRAY(Integer)), nullable=False)
    add_date = Column(DateTime, nullable=False, default=func.now())

    # 관계 설정
    company = relationship("CompanyID", backref="tag_relations")