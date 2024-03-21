import os
import sqlalchemy as sa
from datetime import datetime
from ..models import ChatHistory
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, create_engine, text


def get_chat_history(employee_id):
    try:
        chat_history = ChatHistory.objects.filter(employee_id_id=employee_id).order_by('timestamp')[:10]
        return chat_history
        
    except Exception as e:
        print("An error occurred:", e)
        return None


def get_postgres_conn():
    try:
        db_url = sa.engine.URL.create(drivername='postgresql+psycopg2',
            username = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            host = os.getenv('DB_HOST'),
            port = os.getenv('DB_PORT'),
            database = os.getenv('DB_NAME'))
        engine = sa.create_engine(db_url)
        return engine
    except Exception as e:
        print("An error occurred:", e)
        return None


def get_stored_skills():
    try:
        engine = get_postgres_conn()
        with engine.connect() as conn:
            result = conn.execute(text("""SELECT LOWER(s."skill_name") FROM botservice_skill s ;"""))
            stored_skills = [row[0] for row in result.fetchall()]
        return stored_skills
    except Exception as e:
        print("An error occurred:", e)
        return None