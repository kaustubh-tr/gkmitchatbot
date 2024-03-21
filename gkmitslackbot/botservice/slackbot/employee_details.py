import os
import json
from ..models import *
from datetime import datetime
from django.db import transaction
from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_USER_TOKEN = os.getenv('SLACK_BOT_USER_TOKEN')
slack_client = WebClient(token=os.getenv('SLACK_BOT_USER_TOKEN'))

def get_slack_user_ids(member_details):
    """Extract slack_user_id from member_details."""
    return [member['id'] for member in member_details if member['name'] not in ['slackbot'] and member['is_bot']==False]

def delete_non_existing_employees(slack_user_ids):
    """Delete employees not found in slack_user_ids."""
    all_employees = Employee.objects.all()
    for employee in all_employees:
        if employee.slack_user_id not in slack_user_ids:
            employee.delete()
            print(f"Deleted employee {employee.slack_user_id} as it was not found in member_details.")

def set_job_level_separately(member):
    title = member['profile']['title'].lower() if member['profile']['title'] else ''
    if 'jr' in title or 'jr.' in title or 'junior' in title:
        job_level = 'junior'
    elif 'sr' in title or 'sr.' in title or 'senior' in title:
        job_level = 'senior'
    elif 'lead' in title:
        job_level = 'lead'
    elif 'intern' in title:
        job_level = 'intern'
    elif not title:
        job_level = ''
    else:
        job_level = 'mid'
    return job_level

def update_or_create_employee(member):
    """Update or create an employee based on member details."""
    try:
        job_level = set_job_level_separately(member)
        existing_employee, created = Employee.objects.get_or_create(
            slack_user_id=member['id'],
            defaults={
                'full_name': member['profile']['real_name'],
                'first_name': member['profile']['first_name'],
                'last_name': member['profile']['last_name'],
                'phone_number': member['profile']['phone'],
                'email_address': member['profile']['email'],
                'job_level': job_level,
                'joining_date': datetime.strptime(member['profile']['start_date'], '%Y-%m-%d') if 'start_date' in member['profile'] else None,
                'designation': member['profile']['title'],
            }
        )
        if created:
            print(f"New employee {member['id']} saved successfully.")
        else:
            update_employee_fields(existing_employee, member)
    except Exception as e:
        print(f"An error occurred while processing member {member['id']}: {e}")

def update_employee_fields(employee, member):
    """Update employee fields if they are missing."""
    with transaction.atomic():
        update_fields = []
        if member['profile']['real_name'] and not employee.full_name:
            employee.full_name = member['profile']['real_name']
            update_fields.append('full_name')
        if member['profile']['first_name'] and not employee.first_name:
            employee.first_name = member['profile']['first_name']
            update_fields.append('first_name')
        if member['profile']['last_name'] and not employee.last_name:
            employee.last_name = member['profile']['last_name']
            update_fields.append('last_name')
        if member['profile']['phone'] and not employee.phone_number:
            employee.phone_number = member['profile']['phone']
            update_fields.append('phone_number')
        if member['profile']['email'] and not employee.email_address:
            employee.email_address = member['profile']['email']
            update_fields.append('email_address')
        if 'start_date' in member['profile'] and member['profile']['start_date'] and not employee.joining_date:
            employee.joining_date = datetime.strptime(member['profile']['start_date'], '%Y-%m-%d')
            update_fields.append('joining_date')
        if member['profile']['title'] and not employee.designation:
            employee.designation = member['profile']['title']
            update_fields.append('designation')
        
        job_level = set_job_level_separately(member)
        if not employee.job_level or employee.job_level != job_level:
            employee.job_level = job_level
            update_fields.append('job_level')
        
        if update_fields:
            employee.save(update_fields=update_fields)
            print(f"Updated employee {member['id']} with missing fields.")
        else:
            print(f"Employee {member['id']} already exists with all fields.")

def process_member_details():
    """Main function to process member_details."""
    try:
        member_list = slack_client.users_list()
        member_details = member_list['members']
        slack_user_ids = get_slack_user_ids(member_details)
        for member in member_details:
            if member['name'] not in ['slackbot'] and member['is_bot']==False :
                update_or_create_employee(member)
        # delete_non_existing_employees(slack_user_ids)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
