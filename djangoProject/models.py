import django.contrib.auth.models
from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(django.contrib.auth.models.User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "note"
