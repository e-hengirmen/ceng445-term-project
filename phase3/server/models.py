from django.db import models

# Create your models here.
class GAME(models.Model):
    game_id = models.AutoField(primary_key=True)
    user_count = models.IntegerField()
    def __str__(self):
        return str(self.game_id)+"\t"+str(self.user_count)