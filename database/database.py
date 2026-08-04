from sqlalchemy import create_engine #connection bw db and py
from sqlalchemy.orm import sessionmaker, declarative_base
database_url = "sqlite:///./knowledge_assistant.db"
engine = create_engine(database_url, connect_args={"check_same_thread": False})
#connect_args db ki additional settings hain
#"check_same_thread": False ---allows db to use multi threads if needed
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine) 
#SESSION MAKER CREATS A MACHINE THAT GENERATE A SESSSION
#auoflush=False --- do not automatically send pending changes to the database before a query.
#bind=engine-- Every session created by SessionLocal() should use this engine.
Base=declarative_base() #Creates the base class for all database models.