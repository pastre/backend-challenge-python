from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import QueryDict

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q

from django.db.utils import IntegrityError 

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import  logout as djangoLogout

from .sign_in_with_apple import *

from  .models import *
import json
import datetime

def getKeyFromBody(request, key):
	try:
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
		return body.get(key)
	except: return None


def fetchObject(obj, objId):

	try:
		ret = obj.objects.get(pk=objId)
		return ret
	except ObjectDoesNotExist:
		return False

def payload(message, status):
	return HttpResponse(
		json.dumps( {"status": status, "payload": message} if not message == None else { "status": status } )
	) 
def error(message): return payload(message, "error")
def success(message = None): return payload(message, "success")

def wrongMethod(): return HttpResponseForbidden('Wrong method, sorry')
def malformedRequest(message = 'malformedRequest'): return HttpResponse(message)
def authenticationNeeded(): return error("Authentication required")

# Fetches a reflection from the DB
def fetchReflection(reflectionId): return fetchObject(Reflection, reflectionId)

# Formats a reflection from the DB
def formattedModel(m): 		return success(m.toDict())
def formattedModelArray(a): return success([ i.toDict() for i in a])
def reflectionsInRange(params):

	if not 'from' in params.keys(): return malformedRequest()
	try:
		start = datetime.datetime.strptime(params["from"][0], "%d%m%Y")
		# start = stringToDatetime(params["from"][0])

		if "to" in params.keys(): end = datetime.datetime.strptime(params["to"][0] + " 23:59:59", "%d%m%Y %H:%M:%S")
		else: end = datetime.datetime.now()

		reflections = Reflection.objects.filter(createdAt__range = (start, end))

		return formattedModelArray(reflections)
	except ValueError:
		return error("Failed to parse date")

# -------- Reflection methods
def createReflection(title, text, owner, isPublic = True): 

	newReflection = Reflection(title = title, content = text, owner = owner, isPublic = isPublic)
	newReflection.save()

	reflection = Reflection.objects.get(pk = newReflection.pk)

	return  success(reflection.toDict())
def updateReflection(reflectionId, newReflection): pass # TODO
def getReflections(user):
	return Reflection.objects.filter(owner = user)

@csrf_exempt 
def reflections(request, reflectionId = None):
	
	if not request.user.is_authenticated: return authenticationNeeded()

	if reflectionId == None: 
		if request.method == 'GET': 
			params = dict(request.GET)
			if len(params.keys()) == 0: return formattedModelArray(Reflection.objects.filter(Q(isPublic = True) | Q(sharedWith__pk__contains = request.user.pk)))
			return reflectionsInRange(params)

		if request.method == 'POST': 
			title = getKeyFromBody(request, "title")
			content = getKeyFromBody(request, "content")
			isPublic = getKeyFromBody(request, "isPublic")

			if not title: return error("Could not find parameter: title")
			if not content: return error("Could not find parameter: content")

			print("TITLE is", title)

			return createReflection(title, content, request.user, True if (isPublic == None or isPublic) else False)
		
		return wrongMethod()


	reflection = fetchReflection(reflectionId)
	if not reflection: return malformedRequest()
	if not reflection.owner == request.user: return error("Not authorized")

	if request.method == 'PUT':

		title = getKeyFromBody(request, "title")
		content = getKeyFromBody(request, "content")
		isPublic = getKeyFromBody(request, "isPublic")

		title = title if title  else reflection.title
		content = content if content  else reflection.content
		isPublic = isPublic if (not isPublic == None)  else reflection.isPublic


		reflection.title = title
		reflection.content = content
		reflection.isPublic = isPublic


		reflection.save()

		return success(Reflection.objects.get(pk = reflection.pk).toDict())

	if request.method == 'GET': return formattedModel(reflection)
	if request.method == 'DELETE':
		reflection.delete()
		return formattedModelArray(getReflections(request.user))

		
		

	return wrongMethod()


# -------- Share reflection methods

def _shareReflection(users, reflection):

	for uId in users:
		try: user = User.objects.get(pk = uId)
		except: continue
		if not user: continue

		reflection.sharedWith.add(user)

	reflection.save()

	return formattedModelArray(reflection.sharedWith.all())
def cancelShare(users, reflection): 

	for uId in users:
		user = User.objects.get(pk = uId)

		if not user: continue

		reflection.sharedWith.remove(user)

	reflection.save()

	return formattedModelArray(reflection.sharedWith.all())

@csrf_exempt
def shareReflection(request, reflectionId):

	if not request.user.is_authenticated: return authenticationNeeded()

	reflection = fetchReflection(reflectionId)

	if not reflection: return malformedRequest()
	if not reflection.owner == request.user: return error("Not authorized")

	if request.method == 'GET': return formattedModelArray(reflection.sharedWith.all())
	
	users = getKeyFromBody(request, 'users')
	if not users: return malformedRequest()

	users.remove(request.user.pk)

	if request.method == 'POST': return _shareReflection(users, reflection)

	if request.method == 'DELETE': return cancelShare(users, reflection)

	return wrongMethod()

@csrf_exempt
def userReflections(request, userId):

	if not request.user.is_authenticated: return authenticationNeeded()
	user = fetchUser(userId)
	
	if not user: return error("User not found")

	isPublic = not (user == request.user)

	reflections = Reflection.objects.filter(owner = user)
	if isPublic: reflections = reflections.filter(isPublic = True)

	return formattedModelArray(reflections)

# -------- User methods
def fetchUser(userId): return fetchObject(User, userId)
def createUserIfPossible(request):

	username = getKeyFromBody(request, 'username')
	password = getKeyFromBody(request, 'password')
	email = getKeyFromBody(request, 'password')

	if not username: return malformedRequest()
	if not password: return malformedRequest()
	if not email: return malformedRequest()

	try:
		user = User.objects.create_user(username = username, email=email, password=password )
		user.save()

		login(request, user)

		return formattedModel(user)

	except IntegrityError: return error("User already exists")

def deleteUserIfPossible(userId):
	user = fetchUser(userId)

	if not user: return error("User not found!")
	user.delete()
	return formattedModel(user)
def usersInRange(params):
	if 'username' in params.keys(): 
		pattern = params["username"][0]
		users = User.objects.filter(username__contains=pattern)

		return formattedModelArray(users)
	return malformedRequest("Use the <i>username</i> parameter to search a user")

@csrf_exempt 
def users(request, userId = None):
	isAuth = request.user.is_authenticated
	# Se nao for post, retorne erro
	if userId == None:
		if request.method == 'GET': 
			if not isAuth: return authenticationNeeded()
			params = dict(request.GET)
			if len(params.keys()) == 0: return formattedModelArray(User.objects.all())

			return usersInRange(params)

		if request.method == 'POST': return createUserIfPossible(request)

		return wrongMethod()

	if not isAuth: return authenticationNeeded()
	if request.method == 'DELETE': return deleteUserIfPossible(userId)
	
	return wrongMethod()
	

# -------- Auth methods
@csrf_exempt
def auth(request):
	if not request.method == 'POST': return wrongMethod()

	username = getKeyFromBody(request, 'username')
	password = getKeyFromBody(request, 'password')

	print(username, password)

	if not username: return malformedRequest()
	if not password: return malformedRequest()

	user = authenticate(request, username=username, password=password)

	if user is not None:
		login(request, user)
		myUser = User.objects.get(pk = user.pk)
		return success(myUser.toDict())

	else: return error("Authentication failed")

@csrf_exempt
def signInWithApple(request):
	if not request.method == 'POST': return wrongMethod()

	authCode = getKeyFromBody(request, "authorizationCode")
	username = getKeyFromBody(request, "username")

	if not authCode: return malformedRequest()

	user = AppleOAuth2().do_auth(authCode, username)
	print("User is", user)

	if not user: return error("Two factor Authentication failed!")
	print("User is", user)
	login(request, user)

	myUser = User.objects.get(pk = user.pk)
	return success(myUser.toDict())


@csrf_exempt
def logout(request):
	djangoLogout(request)

	return success()