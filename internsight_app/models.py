from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    skills = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
    
class Internship(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    apply_link = models.URLField()
    source = models.CharField(max_length=100, blank=True, null=True)
    extracted_skills = models.JSONField(blank=True, null=True)