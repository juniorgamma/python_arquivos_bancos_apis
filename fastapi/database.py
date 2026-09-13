from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)        # motor - comunica banco de dados com fastapi
SessionLocal = sessionmaker(bind = engine)  # cria conexão com o banco de dados

Base = declarative_base()  # serve para que possamos criar os modelos