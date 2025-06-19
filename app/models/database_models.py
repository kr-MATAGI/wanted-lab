from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Column, Integer, Text, ForeignKey, ARRAY, DateTime, func
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


class CompanyName(Base):
    """회사 정보 모델"""
    __tablename__ = "tbl_company_names"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    company_id = Column(
        Integer,
        ForeignKey("tbl_company_ids.id"),
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


class Tag(Base):
    """태그 정보 모델"""
    __tablename__ = "tbl_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(Text, nullable=False)
    company_ids = Column(MutableList.as_mutable(ARRAY(Integer)), nullable=False)
    language_id = Column(
        Integer, 
        ForeignKey("tbl_languages.id"),
    )
    add_date = Column(DateTime, nullable=False, default=func.now())

    # 관계 설정
    language = relationship("Language", backref="tags")