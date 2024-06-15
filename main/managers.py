from django.db import models 

class CourseManager(models.Manager):
    def get_queryset(self):
        # Filter out Microsoft courses
        return super().get_queryset().exclude(provider='Microsoft')