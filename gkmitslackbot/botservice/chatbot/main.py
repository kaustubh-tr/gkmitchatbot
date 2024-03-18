import os
import langchain
langchain.debug=False

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import Field
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, tool
from django.db import transaction
from langchain.prompts.chat import (
    SystemMessagePromptTemplate as SystemTemplate,
    HumanMessagePromptTemplate as HumanTemplate,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.memory import ChatMessageHistory
from datetime import datetime

from ..models import ChatHistory
from .templates import SYSTEM_MESSAGE
from .tools import get_employee_by_skill_tool
from .utils import get_chat_history, get_postgres_conn, get_stored_skills
from .others import save_conversation_in_database, get_related_skill_from_llm

load_dotenv()
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
openai_api_key = os.getenv('OPENAI_API_KEY')

class GkmitChatBot:
    def __init__(self):
        self.llm = self.get_llm()

    def get_llm(self):
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        return llm

    def get_tool_list(self, employee_id) -> list:
        employee_by_skill_search_tool = get_employee_by_skill_tool(employee_id)
        return [
            employee_by_skill_search_tool,
        ]

    def get_response(self, question, employee_id):
        try:
            system_message_template = SystemTemplate.from_template(SYSTEM_MESSAGE)
            system_message = system_message_template.format()
            
            history = self.add_chat_history_to_agent(employee_id)
            agent_kwargs = {
                "system_message": system_message,
                "extra_prompt_messages": history.messages,
            }
            tools = self.get_tool_list(employee_id)
            agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.OPENAI_FUNCTIONS,
                verbose=True,
                agent_kwargs=agent_kwargs,
                return_intermediate_steps=True
            )
            answer = agent.invoke(question)

            save_conversation_in_database({
                "message": question,
                "response": answer['output'],
                "employee_id_id": employee_id
            })

            return answer

        except Exception as e:
            return "Sorry, I am unable to answer this question."

    def add_chat_history_to_agent(self, employee_id) -> ChatMessageHistory:
        chat_history = get_chat_history(employee_id)
        if chat_history is None:
            chat_history = []

        history = ChatMessageHistory()
        for chat in chat_history:
            history.add_user_message(chat.message)
            history.add_ai_message(chat.response)
        return history


if __name__ == "__main__":
    chat_bot = GkmitChatBot()