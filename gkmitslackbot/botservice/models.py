from django.db import models

# Create your models here.

class employee(models.Model):
    id = models.CharField(primary_key=True, max_length=20, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email_address = models.EmailField(max_length=100, blank=True, null=True)
    joining_date = models.DateField()
    job_level = models.CharField(max_length=50, blank=True, null=True)
    is_remote_employee = models.BooleanField()
    job_description = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.first_name

class skill(models.Model):
    id = models.AutoField(primary_key=True)
    skill_name = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.skill_name

class emp_skill(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(employee, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(skill, on_delete=models.CASCADE)
    skill_proficiency = models.CharField(max_length=50, blank=True, null=True)

class project(models.Model):
    id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100, blank=True, null=True)
    is_live = models.BooleanField()
    description = models.CharField(max_length=255)
    def __str__(self):
        return self.project_name

class emp_project(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(employee, on_delete=models.CASCADE)
    project_id = models.ForeignKey(project, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, null=True)

class chat_history(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.ForeignKey(employee, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Chat History Entry {self.id}"
