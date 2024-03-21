import os
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, create_engine, text
from pydantic import Field
from datetime import datetime
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool
from ..models import Employee, Skill
from .utils import get_postgres_conn, get_stored_skills
from .others import get_related_skill_from_llm, find_most_similar_name, find_most_similar_skill
from .queries import (
    GET_EMPLOYEE_BY_SKILL_QUERY, 
    SKILL_EXISTS_QUERY, 
    EMPLOYEE_EXISTS_QUERY, 
    GET_SKILL_BY_EMPLOYEE_QUERY, 
    GET_SKILL_BY_MY_NAME_QUERY
)
from .templates import EMPLOYEE_SEARCH_BY_SKILL_DESC, SKILL_SEARCH_BY_EMPLOYEE_DESC

def get_employee_by_skill_tool(employee_id):
    def get_employee_from_database_tool(skill: str = Field(description="skill"), employee: str = Field(description="employee_id")):
        stored_skills = list(Skill.objects.values_list('skill_name', flat=True))
        engine = get_postgres_conn()
        with engine.connect() as conn:
            query = SKILL_EXISTS_QUERY.format(skill=skill, employee_id=employee_id)
            skill_exists = conn.execute(sa.text(query)).scalar()
            if skill_exists:
                query = GET_EMPLOYEE_BY_SKILL_QUERY.format(skill=skill, employee_id=employee_id)
                temp = pd.read_sql(query, conn)
                return temp.to_dict(orient='records')
            else:
                most_similar_skill = find_most_similar_skill(skill, stored_skills)
                if most_similar_skill == None:
                    most_similar_skill = get_related_skill_from_llm(skill, stored_skills)
                print(f"The most related stored skill to '{skill}' is '{most_similar_skill}'")
                query = GET_EMPLOYEE_BY_SKILL_QUERY.format(skill=most_similar_skill, employee_id=employee_id)
                temp = pd.read_sql(query, conn)
                return temp.to_dict(orient='records')
        
    employee_by_skill_search_tool = Tool(
        name="EMPLOYEE_SEARCH_BY_SKILL",
        func=get_employee_from_database_tool,
        description=EMPLOYEE_SEARCH_BY_SKILL_DESC.format(employee_id=employee_id),
    )
    return employee_by_skill_search_tool


def get_skill_by_employee_tool(employee_id):
    def get_skill_from_database_tool(name: str = Field(description="name"), employee: str = Field(description="employee_id")):
        employee_names = list(Employee.objects.values_list('full_name', flat=True))
        engine = get_postgres_conn()
        with engine.connect() as conn:
            if name == str(employee_id):
                query = GET_SKILL_BY_MY_NAME_QUERY.format(name=name)
                temp = pd.read_sql(query, conn)
                return temp.to_dict(orient='records')
            else:
                query = EMPLOYEE_EXISTS_QUERY.format(name=name)
                employee_exists = conn.execute(sa.text(query)).scalar()
                if employee_exists:
                    query = GET_SKILL_BY_EMPLOYEE_QUERY.format(name=name)
                    temp = pd.read_sql(query, conn)
                    return temp.to_dict(orient='records')
                else:
                    most_similar_employee = find_most_similar_name(name, employee_names)
                    print(f"The most similar employee to '{name}' is '{most_similar_employee}'")
                    query = GET_SKILL_BY_EMPLOYEE_QUERY.format(name=most_similar_employee)
                    temp = pd.read_sql(query, conn)
                    return temp.to_dict(orient='records')

    skill_by_employee_search_tool = Tool(
        name="SKILL_SEARCH_BY_EMPLOYEE",
        func=get_skill_from_database_tool,
        description=SKILL_SEARCH_BY_EMPLOYEE_DESC.format(employee_id=employee_id),
    )
    return skill_by_employee_search_tool
