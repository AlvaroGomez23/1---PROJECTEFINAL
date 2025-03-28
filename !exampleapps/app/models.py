from django.db import models

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)


    def __str__(self):
        return self.title