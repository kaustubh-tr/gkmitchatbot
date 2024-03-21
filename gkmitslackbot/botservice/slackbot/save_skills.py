import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django.conf import settings
from django.utils import timezone
from django.db import transaction, IntegrityError
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from ..models import *
from dotenv import load_dotenv
load_dotenv()


def save_skills_to_database(skill_list, employee_id):
    with transaction.atomic():
        try:
            for skill in skill_list:
                skill = skill.lower()
                skill_exists = Skill.objects.filter(skill_name__iexact=skill).exists()

                if not skill_exists:
                    new_skill = Skill.objects.create(skill_name=skill)
                    EmpSkill.objects.create(employee_id_id=employee_id, skill_id_id=new_skill.id)
                    print("Skill successfully saved and link to employee")
                else:
                    existing_skill = Skill.objects.get(skill_name__iexact=skill)
                    emp_skill_exists = EmpSkill.objects.filter(employee_id_id=employee_id, skill_id_id=existing_skill.id).exists()
                    if not emp_skill_exists:
                        EmpSkill.objects.create(employee_id_id=employee_id, skill_id_id=existing_skill.id)
                        print("Skill successfully linked to employee")
                    else:
                        print("Skill already exists")
        except IntegrityError as e:
            print(f"An integrity error occurred while saving skills for Employee ID {employee_id}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving skills for Employee ID {employee_id}: {e}")
