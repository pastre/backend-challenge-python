from django.db.models import Model, CharField, IntegerField, ForeignKey, DateTimeField, BooleanField, EmailField, CASCADE, ManyToManyField
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User as AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser

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
class TwoFAUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
	uid = CharField(max_length = 10000, null = True)

	username = CharField(max_length = 10000, null = True)
	
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    REQUIRED_FIELDS = []


class Reflection(Model):
	title = CharField(max_length = 10000, null = True)
	content = CharField(max_length = 10000)
	createdAt = DateTimeField(null=True, blank=True, auto_now = True)

	owner = ForeignKey(User, on_delete = CASCADE, null = True,  related_name = "owner")
	sharedWith = ManyToManyField(User,  related_name = "sharedWith", blank = True, null = True)


	isPublic = BooleanField(default = True)

	def toDict(self):
		return  {
			"id": self.pk,
			"title" : self.title,
			"content": self.content,
			"createdAt": self.createdAt.timestamp(),
			"isPublic": self.isPublic,
			'owner': self.owner.toDict()
		}

