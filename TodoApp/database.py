from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./todosapp.db"

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# sqlite commands:
#   1. .schema -> show the schema of the current database
#   2. .mode table -> show all select output in table format in the terminal
#   3. select * from table_name