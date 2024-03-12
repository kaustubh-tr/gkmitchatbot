import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .main import GkmitChatBot
from slack_sdk.signature import SignatureVerifier
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
load_dotenv()

SIGNING_SECRET = os.getenv('SIGNING_SECRET')
signature_verifier = SignatureVerifier(SIGNING_SECRET)
SLACK_BOT_USER_TOKEN = os.getenv('SLACK_BOT_USER_TOKEN')
slack_client = WebClient(token=os.getenv('SLACK_BOT_USER_TOKEN'))

response = slack_client.auth_test()
bot_id = response['user_id']
print('bot_id', bot_id)

# @csrf_exempt
# def slack_events(request):
#     if not signature_verifier.is_valid_request(request.body, request.headers):
#         return JsonResponse({'error': 'invalid request'}, status=400)

#     payload = json.loads(request.body)
#     event = payload.get('event', {})
#     user_id = event.get('user')
#     text = event.get('text')
#     channel_id = event.get('channel')

#     if user_id != None and bot_id != user_id:
#         if text:
#             chat_bot = GkmitChatBot()
#             answer = chat_bot.get_response(text)
#             final_answer = answer['output']
#             print("final answer --", final_answer)
#             # send_message_to_slack(channel_id, final_answer)

#     return JsonResponse({'status': 'ok'})
    
# def send_message_to_slack(channel_id, message_text):
#     try:
#         response = slack_client.chat_postMessage(
#             channel=channel_id,
#             text=message_text
#         )
#     except SlackApiError as e:
#         print(f"Got an error: {e.response['error']}")


# bot_id = slack_client.auth_test()['user_id']
# # print('bot_id', bot_id)

@csrf_exempt
def slack_events(request):
    if not signature_verifier.is_valid_request(request.body, request.headers):
        return JsonResponse({'error': 'invalid request'}, status=400)

    payload = json.loads(request.body)
    # print('payload:', payload)
    event = payload.get('event', {})
    user_id = event.get('user')
    text = event.get('text')
    print('text:', text)
    channel_id = event.get('channel')
    print('channel_id:', channel_id)
    print('user_id--', user_id)
    print(bot_id != user_id)
    slack_message = request.data
    print('slack_message', slack_message)
   
    if user_id and text and (bot_id != user_id):
        result = slack_client.users_info(user=user_id)
        first_name = result['user']['profile']['first_name']
        last_name = result['user']['profile']['last_name']
        job_description = result['user']['profile']['title']
        phone_number = result['user']['profile']['phone']
        email_address = result['user']['profile']['email']
        print("user_id:", user_id)
        print("first_name:", first_name)
        print("last Name:", last_name)
        print("job_description:", job_description)
        print("phone_number:", phone_number)
        print("email_address:", email_address)

        thread = threading.Thread(target=send_response, args=(text, channel_id,))
        thread.start()
        return JsonResponse({'status': 'ok'}, status=200)
    else:
        return JsonResponse({'status': 'ok'}, status=200)
        # Log the error or handle it as needed
    return JsonResponse({'status': 'ok'}, status=200)


def send_response(text, channel_id):
    # chat_bot = GkmitChatBot()
    # answer = chat_bot.get_response(text)
    # final_answer = answer['output']
    final_answer = "Hello, user!"
    response = slack_client.chat_postMessage(channel=channel_id, text=final_answer)