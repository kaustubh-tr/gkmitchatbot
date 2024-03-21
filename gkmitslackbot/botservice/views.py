import os
import re
import json
import logging
import time
import threading
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.db.models import Q
from .models import *
from .chatbot.main import GkmitChatBot
from slack_sdk.signature import SignatureVerifier
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import langchain
langchain.debug = False
from .slackbot.employee_details import (
    get_slack_user_ids, 
    delete_non_existing_employees, 
    update_or_create_employee, 
    update_employee_fields, 
    process_member_details,
)
from .slackbot.save_skills import save_skills_to_database
from .slackbot.others import add_chat_history_to_conversation_memory, get_skill_list_from_llm

load_dotenv()
output_parser = StrOutputParser()
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=200)
openai_api_key = os.getenv('OPENAI_API_KEY')

SIGNING_SECRET = os.getenv('SIGNING_SECRET')
signature_verifier = SignatureVerifier(SIGNING_SECRET)
SLACK_BOT_USER_TOKEN = os.getenv('SLACK_BOT_USER_TOKEN')
slack_client = WebClient(token=os.getenv('SLACK_BOT_USER_TOKEN'))

# process_member_details()
bot_id = slack_client.auth_test()['user_id']

def convert_to_markdown(text):
    pattern = r'\*\*([^*]+)\*\*'
    return re.sub(pattern, r'*\1*', text)


@csrf_exempt
def handle_slack_events(request):
    """Handle Slack events, including processing messages."""
    if not signature_verifier.is_valid_request(request.body, request.headers):
        return JsonResponse({'error': 'invalid request'}, status=400)
    
    # # URL Verification
    # if request.method == 'POST':
    #     try:
    #         data = json.loads(request.body)
    #         challenge = data.get('challenge')
    #         if challenge:
    #             # Respond with the challenge token
    #             return JsonResponse({'code': 200, 'body': {'challenge': challenge}})
    #         else:
    #             # Challenge verification failed
    #             return JsonResponse({'code': 400, 'error': 'challenge_failed', 'body': {}}, status=400)
    #     except json.JSONDecodeError:
    #         # Invalid JSON format
    #         return JsonResponse({'code': 400, 'error': 'invalid_json', 'body': {}}, status=400)
    # else:
    #     # Invalid request method
    #     return JsonResponse({'code': 405, 'error': 'invalid_request_method', 'body': {}}, status=405)

    payload = json.loads(request.body)
    event = payload.get('event', {})
    slack_user_id = event.get('user')
    text = event.get('text')
    channel_id = event.get('channel')

    if slack_user_id and text and (bot_id != slack_user_id):
        thread = threading.Thread(target=send_response_to_slack, args=(text, slack_user_id, channel_id,))
        thread.start()
        return JsonResponse({'status': 'ok'}, status=200)
    else:
        return JsonResponse({'status': 'ok'}, status=200)


def send_response_to_slack(text, slack_user_id, channel_id):
    """Send a response to a Slack message."""
    try:
        employee = Employee.objects.get(slack_user_id=slack_user_id)
    except ObjectDoesNotExist:
        print(f"No employee found for Slack user ID: {slack_user_id}")
        return
    chat_bot = GkmitChatBot()
    answer = chat_bot.get_response(text, employee.id)
    if answer == "Sorry, I am unable to answer this question." :
        final_answer = answer
    else:
        final_answer = convert_to_markdown(answer['output'])
    response = slack_client.chat_postMessage(channel=channel_id, text=final_answer)

    skill_list = get_skill_list_from_llm(text, employee.id)
    if skill_list:
        save_skills_to_database(skill_list, employee.id)
    return JsonResponse({'status': 'ok'}, status=200)

