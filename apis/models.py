from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')), max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')
