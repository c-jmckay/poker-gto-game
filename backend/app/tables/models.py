import uuid

from django.db import models

# Create your models here.
class PokerTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_token = models.UUIDField(db_index=True)
    human_seat_id = models.PositiveIntegerField()
    snapshot = models.JSONField()
    revision = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.owner_token
