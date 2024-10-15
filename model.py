from .database import Base
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class Password(Base):
    __tablename__ = "pw_db"

    id = Column(Integer, primary_key=True, nullable=False)
    Type = Column(String, nullable=False)
    Password = Column(String, nullable=False)
    Created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
