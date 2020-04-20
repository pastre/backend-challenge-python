from django.db.models import Model, CharField, IntegerField, ForeignKey, DateTimeField, BooleanField, EmailField, CASCADE, ManyToManyField
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User as AbstractUser

# Entrypoint para extendermos um usuario
class User(AbstractUser):

	class Meta:
		proxy = True
		ordering = ('username', )

	def toDict(self):
		return {
			"username": self.username,
			"id": self.pk,
			"email": self.email,
		}

class Reflection(Model):
	content = CharField(max_length = 10000)
	createdAt = DateTimeField(null=True, blank=True, auto_now = True)

	owner = ForeignKey(User, on_delete = CASCADE, null = True,  related_name = "owner")
	sharedWith = ManyToManyField(User,  related_name = "sharedWith")


	isPublic = BooleanField(default = True)

	def toDict(self):
		return  {
			"id": self.pk,
			"content": self.content,
			"createdAt": self.createdAt.timestamp(),
			"isPublic": self.isPublic,
			'owner': self.owner.toDict()
		}

