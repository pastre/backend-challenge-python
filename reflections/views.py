from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseForbidden
from django.http import QueryDict

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.db.utils import IntegrityError 

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import  logout as djangoLogout

from  .models import *

import json
import datetime

def getKeyFromBody(request, key):	
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	return body.get(key)


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
def createReflection(text, owner, isPublic = True): 
	print("isPublic", isPublic)
	newReflection = Reflection(content = text, owner = owner, isPublic = isPublic)
	newReflection.save()
	reflection = Reflection.objects.get(pk = newReflection.pk)
	return  success({"reflection": (reflection.toDict())})

def updateReflection(reflectionId, newReflection): pass # TODO
def getReflections(user):
	return Reflection.objects.filter(owner = user)

@csrf_exempt 
def reflections(request, reflectionId = None):
	
	if not request.user.is_authenticated: return authenticationNeeded()

	if reflectionId == None: 
		if request.method == 'GET': 
			params = dict(request.GET)
			if len(params.keys()) == 0: return formattedModelArray(getReflections(request.user))
			return reflectionsInRange(params)

		if request.method == 'POST': 
			content = request.POST.get("content")
			isPublic = request.POST.get("isPublic")
			if not content: return error("porra brow")
			return createReflection(content, request.user, True if (isPublic == None or isPublic) else False)
		
		return wrongMethod()


	reflection = fetchReflection(reflectionId)
	if not reflection: return malformedRequest()
	if not reflection.owner == request.user: return error("Not authorized")

	if request.method == 'PUT': pass # TODO
	if request.method == 'GET': return formattedModel(reflection)
	if request.method == 'DELETE':
		reflection.delete()
		return formattedModelArray(getReflections(request.user))

		
		

	return wrongMethod()


# -------- Share reflection methods

def _shareReflection(users, reflection):

	for uId in users:
		user = User.objects.get(pk = uId)

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


# -------- User methods
def fetchUser(userId): return fetchObject(User, userId)
def createUserIfPossible(request):
	payload = request.POST
	required = ['username', 'email', 'password',]
	
	# Se esta faltando algum parametro, retorne erro
	for req in required: 
		if not req in payload.keys(): return malformedRequest()

	username, email, password = [payload.get(i) for i in required]

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
	if not request.method == 'POST': wrongMethod()

	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)

	if user is not None:
		login(request, user)
		myUser = User.objects.get(pk = user.pk)
		return success({"user": myUser.toDict()})

	else: return error("Authentication failed")


@csrf_exempt
def logout(request):
	djangoLogout(request)

	return success()