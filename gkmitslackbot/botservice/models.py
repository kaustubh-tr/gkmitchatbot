import uuid
from django.db import models

# Create your models here.

class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    # id = models.AutoField(primary_key=True)
    slack_user_id = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email_address = models.EmailField(max_length=100, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    job_level = models.CharField(max_length=50, blank=True, null=True)
    is_remote_employee = models.BooleanField(blank=True, null=True)
    job_description = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.first_name

class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    skill_name = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.skill_name

class EmpSkill(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_proficiency = models.CharField(max_length=50, blank=True, null=True)

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100, blank=True, null=True)
    is_live = models.BooleanField(blank=True, null=True)
    description = models.CharField(max_length=255)
    def __str__(self):
        return self.project_name

class EmpProject(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, null=True)

class ChatHistory(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Chat History Entry {self.id}"
