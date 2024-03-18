import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, create_engine, text
from pydantic import Field
from datetime import datetime
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool
from .utils import get_postgres_conn, get_stored_skills
from .others import get_related_skill_from_llm
from .queries import GET_EMPLOYEE_BY_SKILL_QUERY, SKILL_EXISTS_QUERY
from .templates import EMPLOYEE_SEARCH_BY_SKILL_DESC

def get_employee_by_skill_tool(employee_id):
    def get_employee_from_database_tool(skill: str = Field(description="skill"), employee: str = Field(description="employee_id")):
        engine = get_postgres_conn()
        with engine.connect() as conn:
            print('skill:', skill)
            query = SKILL_EXISTS_QUERY.format(skill=skill, employee_id=employee_id)
            skill_exists = conn.execute(sa.text(query)).scalar()
            if skill_exists:
                query = GET_EMPLOYEE_BY_SKILL_QUERY.format(skill=skill, employee_id=employee_id)
                temp = pd.read_sql(query, conn)
                return temp.to_dict(orient='records')
            else:
                stored_skills = get_stored_skills()
                related_skill = get_related_skill_from_llm(skill, stored_skills)
                print(f"The most related stored skill to '{skill}' is '{related_skill}'")
                query = GET_EMPLOYEE_BY_SKILL_QUERY.format(skill=related_skill, employee_id=employee_id)
                temp = pd.read_sql(query, conn)
                return temp.to_dict(orient='records')
    employee_by_skill_search_tool = Tool(
        name="EMPLOYEE_SEARCH_BY_SKILL",
        func=get_employee_from_database_tool,
        description=EMPLOYEE_SEARCH_BY_SKILL_DESC.format(employee_id=employee_id),
    )
    return employee_by_skill_search_tool