from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
# Create your models here.
User = get_user_model()
class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=15)
    department = models.CharField(max_length=100, default='No department')
    semester = models.IntegerField(default=1)
    class_name = models.CharField(max_length=20)
    roll_no = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.first_name 
    
    
class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=15)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.first_name 
        
class Teacher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=15)
    department = models.CharField(max_length=100, default='No department')
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.first_name 

class Markpresence(models.Model):
  #  class_name = models.CharField(max_length=200)  # adjust as needed
   # roll_no = models.IntegerField()
    image = models.ImageField(upload_to="validation")
    video = models.FileField(upload_to="validation_video")  
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(updated_at)

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)   
    type = models.CharField(max_length=15)
    department = models.CharField(max_length=100, default='No department')
    semester = models.IntegerField()
    class_name = models.CharField(max_length=20)
    roll_no = models.CharField(max_length=100)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.DateTimeField()
    def __str__(self):
        return f"{self.student} {self.date} {self.time}"

class CameraImg(models.Model):
     username = models.CharField(max_length=30)
     image = models.ImageField(upload_to="validation")


class CapturedImage(models.Model):
    image = models.ImageField(upload_to='db_facerecog/training_video/')
    timestamp = models.DateTimeField(auto_now_add=True)


class Application(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
 
    def __str__ (self):
        return str(self.applicant)
