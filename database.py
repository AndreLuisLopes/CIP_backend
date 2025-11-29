import os

from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker, scoped_session

from dotenv import load_dotenv

from flask import g



load_dotenv()





DATABASE_URL = os.getenv(

    "DATABASE_URL",

    "mysql+pymysql://root:123456789@localhost:3306/credenciamento"

)





engine = create_engine(

    DATABASE_URL,

    pool_pre_ping=True,          

    pool_size=10,                

    max_overflow=20,             

    pool_timeout=30,             

    pool_recycle=1800,           

)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()



def init_db():

    """Inicializa o banco de dados"""

    Base.metadata.create_all(bind=engine)



def get_db():

    """Obtém sessão do banco para Flask"""

    if 'db' not in g:

        g.db = db_session()

    return g.db



def close_db(e=None):

    """Fecha a sessão do banco"""

    

    

    

    

    db = g.pop('db', None)

    if db is not None:

        try:

            db.close()

        except Exception:

            pass

    

    

    db_session.remove()

