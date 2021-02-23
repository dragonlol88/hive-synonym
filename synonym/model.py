from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

ModelBase = declarative_base()

engine = create_engine('mysql+pymysql://ta_dev:elastic!@#@192.168.0.220/elastic_synonym')
Session = sessionmaker(bind=engine)
session = Session()


class User(ModelBase):
    __tablename__ = 'tbl_user_mocking'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(String(64), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class ProjectUser(ModelBase):
    __tablename__ = 'tbl_project_user_mocking'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('tbl_user_mocking.id'))
    pjt_id = Column(Integer, ForeignKey('tbl_pjt_mocking.id'))
    project = relationship('Project', uselist=False, cascade="all,delete")



class Project(ModelBase):
    __tablename__ = 'tbl_pjt_mocking'
    id = Column(Integer, autoincrement=True, primary_key=True)
    pjt_name = Column(String(128), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(String(64), server_default=func.now(), onupdate=func.now())

    pjt_user = relationship('ProjectUser', uselist=True, cascade="all,delete")
    synonym = relationship('Synonym', uselist=True, cascade="all,delete")
    origin = relationship('Origin', uselist=True, cascade="all,delete")
    category = relationship('Category', uselist=True, cascade="all,delete")

class Category(ModelBase):
    __tablename__ = 'tbl_category_mocking'
    id = Column(Integer, autoincrement=True, primary_key=True)
    category_name = Column(String(128), nullable=False, unique=True)
    pjt_id = Column(Integer, ForeignKey('tbl_pjt_mocking.id'))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=True)
    origin = relationship('Origin', uselist=True, cascade="all,delete")
    synonym = relationship('Synonym', uselist=True, cascade="all,delete")

class Origin(ModelBase):
    __tablename__ = 'tbl_origin_mocking'
    #하나의 category에 하나의 origin constrained 걸
    id = Column(Integer, autoincrement=True, primary_key=True)
    category_id = Column(Integer, ForeignKey('tbl_category_mocking.id'), nullable=False)
    pjt_id = Column(Integer, ForeignKey('tbl_pjt_mocking.id'), nullable=False)
    origin_keyword = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=True)
    synonym = relationship('Synonym', uselist=True, cascade="all,delete",
                           foreign_keys='[Synonym.origin_id]')

class Synonym(ModelBase):
    __tablename__ = 'tbl_synonym_mocking'
    # pjt_id, category_id 같이
    id = Column(Integer, autoincrement=True, primary_key=True)
    pjt_id = Column(Integer, ForeignKey('tbl_pjt_mocking.id'))
    category_id = Column(Integer, ForeignKey('tbl_category_mocking.id'))
    origin_id = Column(Integer, ForeignKey('tbl_origin_mocking.id'))
    synm_keyword = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


# ModelBase.metadata.create_all(engine)
