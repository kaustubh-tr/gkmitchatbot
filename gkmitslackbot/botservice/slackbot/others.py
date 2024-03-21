import os
import ast
import json
from ..models import *
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ChatMessageHistory
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
output_parser = StrOutputParser()
from ..chatbot.main import GkmitChatBot
from ..chatbot.templates import GET_SKILL_LIST_TEMPLATE, GET_SKILL_LIST_PROMPT_MESSAGE
from ..chatbot.utils import get_chat_history

SLACK_BOT_USER_TOKEN = os.getenv('SLACK_BOT_USER_TOKEN')
slack_client = WebClient(token=os.getenv('SLACK_BOT_USER_TOKEN'))

llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=200)
openai_api_key = os.getenv('OPENAI_API_KEY')


def add_chat_history_to_conversation_memory(employee_id)-> ConversationBufferMemory:
    """Add chat history to the conversation memory for a given employee."""
    chat_history = get_chat_history(employee_id)
    if chat_history is None:
        chat_history = []
    memory = ConversationBufferMemory(memory_key="chat_history")
    for chat in chat_history:
        memory.chat_memory.add_user_message(chat.message)
        memory.chat_memory.add_ai_message(chat.response)
    return memory


def get_skill_list_from_llm(text, employee_id):
    """Extract a list of skills from the LLM based on the provided text and employee ID."""
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
        formatted_messages = [("system", GET_SKILL_LIST_TEMPLATE)] + GET_SKILL_LIST_PROMPT_MESSAGE + [("user", "{question}")]
        prompt = ChatPromptTemplate.from_messages(formatted_messages)
        memory = add_chat_history_to_conversation_memory(employee_id)
        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=False,
            memory=memory
        )
        content = conversation.invoke({"question": text})
        output = content['text'].split('\n')[-2]
        skill_list = ast.literal_eval(output.strip("'"))
        return skill_list
    except Exception as e:
        print("An error occurred:", e)
        return None


def schedule_message_to_employees():
    """Send a scheduled message to all employees."""
    slack_user_ids = list(Employee.objects.values_list('slack_user_id', flat=True))
    for user_id in slack_user_ids:
        slack_client.chat_postMessage(channel=user_id, text="Hey, are you currently learning any new skills or do you have expertise in any skills?")
    return "Scheduled message sent!"