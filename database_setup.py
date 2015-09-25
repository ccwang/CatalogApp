from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)


class Item(Base):
    __tablename__ = 'items'

    name =Column(String(500), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(1000))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)




engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)