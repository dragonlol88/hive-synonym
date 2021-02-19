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

engine = create_engine('mysql+pymysql://sunny:chldydtjs1#@127.0.0.1/es-synonym')
Session = sessionmaker(bind=engine)
session = Session()


class User(ModelBase):
    __tablename__ = 'tbl_user'
    user_id = Column(Integer, primary_key=True)
    user = Column(String(128), nullable=False)


class ProjectUser(ModelBase):
    __tablename__ = 'tbl_project_user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('tbl_user.user_id'))
    pjt_id = Column(Integer, ForeignKey('tbl_pjt.id'))
    project = relationship('Project', uselist=False, cascade="all,delete")



class Project(ModelBase):
    __tablename__ = 'tbl_pjt'
    id = Column(Integer, autoincrement=True, primary_key=True)
    pjt_name = Column(String(128), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(String(64), server_default=func.now(), onupdate=func.now())

    pjt_user = relationship('ProjectUser', uselist=True, cascade="all,delete")
    synonym = relationship('Synonym', uselist=True, cascade="all,delete")
    origin = relationship('Origin', uselist=True, cascade="all,delete")
    cartegory = relationship('Cartegory', uselist=True, cascade="all,delete")

class Cartegory(ModelBase):
    __tablename__ = 'tbl_cartegory'
    id = Column(Integer, autoincrement=True, primary_key=True)
    cartegory_name = Column(String(128), nullable=False, unique=True)
    pjt_id = Column(Integer, ForeignKey('tbl_pjt.id'))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=True)
    origin = relationship('Origin', uselist=True, cascade="all,delete")
    synonym = relationship('Synonym', uselist=True, cascade="all,delete")

class Origin(ModelBase):
    __tablename__ = 'tbl_origin'
    #하나의 category에 하나의 origin constrained 걸
    id = Column(Integer, autoincrement=True, primary_key=True)
    cartegory_id = Column(Integer, ForeignKey('tbl_cartegory.id'), nullable=False)
    pjt_id = Column(Integer, ForeignKey('tbl_pjt.id'), nullable=False)
    origin_keyword = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), nullable=True)
    synonym = relationship('Synonym', uselist=True, cascade="all,delete",
                           foreign_keys='[Synonym.origin_id]')

class Synonym(ModelBase):
    __tablename__ = 'tbl_synonym'
    # pjt_id, category_id 같이
    id = Column(Integer, autoincrement=True, primary_key=True)
    pjt_id = Column(Integer, ForeignKey('tbl_pjt.id'))
    cartegory_id = Column(Integer, ForeignKey('tbl_cartegory.id'))
    origin_id = Column(Integer, ForeignKey('tbl_origin.id'))
    synm_keyword = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)


ModelBase.metadata.create_all(engine)
# print(dir(ProjectUser))
# print(dir(ProjectUser.project))
# print(dir(ProjectUser.pjt_id))
# print(hasattr(ProjectUser.project, 'entity'))
# print(hasattr(ProjectUser.pjt_id, 'entity'))
# print(ProjectUser.project)
# print(ProjectUser.pjt_id)
# print('1',dir(ProjectUser.project.entity))
# print('1',ProjectUser.project.entity.class_.__name__)

# print('2',ProjectUser.metadata.tables)
# print('3',ProjectUser.metadata)
# print('4',ProjectUser.metadata)
# print('5',ProjectUser.metadata)
# print('6',ProjectUser.metadata)
# print('7',ProjectUser.metadata)
# # Base.metadata.create_all(engine)
#
# from pydantic import BaseModel
# from datetime import datetime
# import typing
# from sqlalchemy import and_, or_
#
# class Projec(BaseModel):
#     pjt_name: str
#     created_at: datetime
#     updated_at: datetime
#     class Config:
#         orm_mode = True
#
# class Resp(BaseModel):
#     project: Projec
#
#     class Config:
#         orm_mode = True
#
# # getattr(ProjectUser, 'user_id')


# fileters = [ProjectUser.user_id==1212323, ProjectUser.pjt_id.in_([1])]
# # filters = [and_(*fileters)]
# # filters.append(ProjectUser.pjt_id==1)
#
# from sqlalchemy import desc
# projects = session.query(ProjectUser).all()
# print(projects)
# #
# projects = [i.project for i in projects]
# #
# for project in projects:
#     print(project)
    # print(project.project[0])
    # Projec.from_orm(project.project[0])
    # print(Resp.from_orm(project).json())
    # res = Resp.from_orm(project)
    # print(res.json())

# project = Project.of(pjt_name='hello')
# project.parti.append(ProjectUser(user_id=123426))
# project.parti.append(ProjectUser(user_id=1234126))
# # project.parti.append(Participants.of(participant='world'))
# # project.parti.append(Participants.of(participant='korea'))
# session.add(project)
# # # fsession.query(Project).filter_by(id=1).fi
# #
# session.commit()

