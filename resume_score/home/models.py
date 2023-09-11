from django.db import models

# Create your models here.
class UploadedFile(models.Model):
    name = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='pdf_files/')
    email=models.CharField(max_length=100)
    job=models.CharField(max_length=100)
    score=models.FloatField()
    status=models.CharField(max_length=20)
    def __str__(self):
        return self.name 

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    score_threshold = models.FloatField()

    def __str__(self):
        return self.title

class Resume(models.Model):
    title = models.CharField(max_length=100)
    skills=models.CharField(max_length=800)

    def __str__(self):
        return self.title
class Application_result(models.Model):
    status=models.CharField(max_length=30)
    title=models.CharField(max_length=100)
    score_threshold=models.FloatField()
    def __str__(self):
        return self.title