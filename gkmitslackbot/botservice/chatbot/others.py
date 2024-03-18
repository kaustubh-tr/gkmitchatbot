import os
import sqlalchemy as sa
from django.db import transaction
from ..models import *
from .utils import get_stored_skills
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, create_engine, text
from .templates import GET_RELATED_SKILL_TEMPLATE, GET_RELATED_SKILL_PROMPT_MESSAGE
load_dotenv()
output_parser = StrOutputParser()
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

def save_conversation_in_database(conversation):
    """Save chat history to the database with the current timestamp."""
    try:
        with transaction.atomic():
            chat_history = ChatHistory.objects.create(
                message=conversation["message"],
                response=conversation["response"],
                timestamp=datetime.now(),
                employee_id_id=conversation["employee_id_id"]
            )
            result = ChatHistory.objects.all().order_by('-timestamp')[:5]
            return result
    except Exception as e:
        print("An error occurred:", e)
        return None

def get_related_skill_from_llm(skill, stored_skills):
    formatted_messages = [{**message, 'content': message['content'].format(stored_skills=stored_skills, skill=skill)} for message in GET_RELATED_SKILL_PROMPT_MESSAGE]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=formatted_messages,
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    content=response.choices[0].message.content
    output = content.split('\n')[-2]
    related_skill = output.strip("'")
    return related_skill