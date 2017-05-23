import os, datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse
from django.shortcuts import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from testsforall.models import Survey, UserTests, Group, Encuesta, Image, Question, Answer, Test, FriendRequest, Result
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
import json
from django.db.models import Q
from django.core import serializers




def index(request):
    
    return render(request, 'testsforall/index.html')


def logoutView(request):
    logout(request)
    messages.info(request, 'Has cerrado sesion correctamente')
    return redirect('testsforall:index')
    
def signup(request):
    return redirect('testsforall:signup')
    
@login_required    
def home(request):
    
    return render(request, 'testsforall/home.html')

    
@login_required
def miCuenta(request):
    
    return render(request, 'testsforall/myaccount.html')
    
    
    
@login_required
def mySurveys(request):
    surveys = Survey.objects.filter(creator = request.user.id)
    return render(request, 'testsforall/mysurveys.html', {'surveys': surveys})
    
@login_required    
def crearEncuesta(request):
    
    usertests = UserTests.objects.get( user_id = request.user.id)
    
    if request.method == "POST":
        
        publishsurvey = False
        
        if request.POST.get('published') == "1":
            publishsurvey = True
        
        
        survey = Encuesta(title = request.POST.get('surveytitle'), creator = usertests, created_at = datetime.datetime.now(),
        last_edition = datetime.datetime.now(), future_publication = request.POST.get('future_publication'),
        future_close = request.POST.get('future_close'), published = publishsurvey, typesurvey = "Encuesta")

        survey.save()
        
        #guardar preguntas
        
        for i in range(int(request.POST.get('totalquestions'))):
            nquestion = i+1
            
            if request.POST.get("inputimgquestion"+str(nquestion)):
                imgquestion = Image.objects.get(id = request.POST.get("inputimgquestion"+str(nquestion)))
                question = Question(title = request.POST.get('tq'+str(nquestion)), survey = survey, image = imgquestion)
                question.save()
            else:
                question = Question(title = request.POST.get('tq'+str(nquestion)), survey = survey)
                question.save()
                
            #guardar respuestas
            for i in range(int(request.POST.get('totalanswers'+str(nquestion)))):
                nanswer = i+1
                ans_que = str(nquestion)+"_"+str(nanswer)
                if request.POST.get("inputimganswer"+ans_que):
                    imganswer = Image.objects.get(id = request.POST.get("inputimganswer"+ans_que))
                    answer = Answer(title = request.POST.get("answer"+ans_que), question = question, image = imganswer)
                    answer.save()
                else:
                    answer = Answer(title = request.POST.get("answer"+ans_que), question = question)
                    answer.save()
            #for i in range(int(request.POST.get('')))
        
        if request.POST.get('inputimgsurvey'):
            survey.image.add(request.POST.get('inputimgsurvey'))
        
        
        return HttpResponseRedirect(reverse('testsforall:survey', kwargs={'idSurvey':survey.id}))
 
    images = Image.objects.filter( uploader = usertests.id);
    context = {'images' : images}
    return render(request, 'testsforall/createencuesta.html', context)
    
    
@login_required
@login_required    
def crearTest(request):
    
    usertests = UserTests.objects.get( user_id = request.user.id)
    
    if request.method == "POST":
        
        publishsurvey = False
        
        if request.POST.get('published') == "1":
            publishsurvey = True
        
        
        survey = Test(title = request.POST.get('surveytitle'), rules = request.POST.get('rules'), creator = usertests, created_at = datetime.datetime.now(),
        last_edition = datetime.datetime.now(), future_publication = request.POST.get('future_publication'),
        future_close = request.POST.get('future_close'), published = publishsurvey, typesurvey = request.POST.get('typetest'))
        survey.save()
        #guardar preguntas
        maxresult = 0
        nquestion = 1
        for i in range(1, int(request.POST.get('totalquestions'))):
            question = None
            while(request.POST.get('tq'+str(nquestion)) is None):
                nquestion = nquestion+1
            if request.POST.get("inputimgquestion"+str(nquestion)):
                imgquestion = Image.objects.get(id = request.POST.get("inputimgquestion"+str(nquestion)))
                question = Question(title = request.POST.get('tq'+str(nquestion)), survey = survey, image = imgquestion, value = request.POST.get('pointsperquestioninput'+str(nquestion)))
                question.save()
            else:
                question = Question(title = request.POST.get('tq'+str(nquestion)), survey = survey, value = request.POST.get('pointsperquestioninput'+str(nquestion)))
                question.save()
            maxresult = maxresult+float(question.value)
            
            correctquestion = request.POST.get('correctanswer'+str(nquestion))
                
            #guardar respuestas
            for i in range(int(request.POST.get('totalanswers'+str(nquestion)))):
                nanswer = i+1
                ans_que = str(nquestion)+"_"+str(nanswer)
                answercorrect = correctquestion == nanswer
                if request.POST.get("inputimganswer"+ans_que):
                    imganswer = Image.objects.get(id = request.POST.get("inputimganswer"+ans_que))
                    
                    answer = Answer(title = request.POST.get("answer"+ans_que), question = question, image = imganswer, correct = answercorrect)
                    answer.save()
                else:
                    answer = Answer(title = request.POST.get("answer"+ans_que), question = question, correct = answercorrect)
                    answer.save()
            #for i in range(int(request.POST.get('')))
        
        if request.POST.get('inputimgsurvey'):
            survey.image.add(request.POST.get('inputimgsurvey'))
        
        survey.max_result = maxresult
        survey.save()
        return HttpResponseRedirect(reverse('testsforall:survey', kwargs={'idSurvey':survey.id}))
 
    images = Image.objects.filter( uploader = usertests.id);
    context = {'images' : images}
    return render(request, 'testsforall/createtest.html', context)

@login_required
def deleteSurvey(request, idSurvey):
    survey = get_object_or_404(Survey, id = idSurvey)
    survey.delete()
    messages.error(request, 'Encuesta eliminada correctamente')
    return HttpResponseRedirect(reverse('testsforall:mySurveys'))

@login_required
def survey(request, idSurvey):
    survey = get_object_or_404(Survey, id=idSurvey)
    return render(request, 'testsforall/viewsurvey.html', {'survey': survey})
    
@login_required    
def creados(request):
    
    tests = Survey.objects.all();
    context = {'tests': tests}
    return render(request, 'testsforall/created.html', context)



def getSurveys(request):
    usertests = UserTests.objects.get(user = request.user.id)
    surveys = Survey.objects.filter(creator = usertests);
    #data = serializers.serialize('json', [obj,])
    #struct = json.loads(data)
    #data = json.dumps(struct[0])
    resposta = list()
    for enquesta in surveys:
        firstimage = str(enquesta.getFirstImage())
        created_date = enquesta.created_at.strftime('%d-%m-%Y')
        last_edition_date = enquesta.last_edition.strftime('%d-%m-%Y')
        if enquesta.future_publication is not None:
            future_publication_date = enquesta.future_publication.strftime('%d-%m-%Y')
        else:
            future_publication_date = 'No hay fecha de publicacion futura'
        if enquesta.future_close is not None:
            future_close_date = enquesta.future_close.strftime('%d-%m-%Y')
        else:
            future_close_date = 'No hay fecha de cierre futura'
        
        resposta.append({
            'id': enquesta.id,
            'typesurvey': enquesta.typesurvey,
            'creator': enquesta.creator.id,
            'title': enquesta.title,
            'created_at': created_date,
            'last_edition': last_edition_date,
            'future_publication': future_publication_date,
            'future_close': future_close_date,
            'published': enquesta.published,
            'image': firstimage
        });
        
    respostaserialitzada = json.dumps(resposta);
    return HttpResponse(respostaserialitzada, content_type='text/json')


@require_POST
def upload( request ):

    # The assumption here is that jQuery File Upload
    # has been configured to send files one at a time.
    # If multiple files can be uploaded simulatenously,
    # 'file' may be a list of files.
    imagen = upload_receive( request )

    usertests = UserTests.objects.get( user_id = request.user.id )
    instance = Image( image = imagen, uploader = usertests )
    instance.save()

    basename = os.path.basename( instance.image.path )
    namepath = "media/"+basename

    file_dict = {
        'name' : basename,
        'size' : imagen.size,
        
        'id' : instance.pk,

        'url': settings.MEDIA_URL + namepath,
        'thumbnailUrl': "/"+settings.MEDIA_URL + namepath,

        'deleteUrl': reverse('testsforall:jfu_delete', kwargs = { 'pk': instance.pk }),
        'deleteType': 'POST',
    }

    return UploadResponse( request, file_dict )

@require_POST
def upload_delete( request, pk ):
    success = True
    try:
        instance = Image.objects.get( pk = pk )
        os.unlink( instance.image.path )
        instance.delete()
    except Survey.DoesNotExist:
        success = False

    return JFUResponse( request, success )
# Create your views here.


@login_required
def publish_survey(request, idSurvey):
    
    surveyToPublish = Survey.objects.get(id = idSurvey)
    surveyToPublish.published = True
    surveyToPublish.save()
    messages.info(request, 'Encuesta publicada correctamente')
    return HttpResponseRedirect(reverse('testsforall:survey', kwargs={'idSurvey':idSurvey}))
    
    
@login_required
def edit_survey(request, idSurvey):
    survey = get_object_or_404(Survey, id = idSurvey)
    if request.method == "POST":
        survey.title = request.POST.get('title')
        survey.last_edition = datetime.datetime.now()
        survey.future_publication = request.POST.get('datepublish')
        if request.POST.get('inputimgsurvey'):
            if survey.getFirstImage is not None:
                survey.images.add(request.POST.get('inputimgsurvey'))
            if request.POST.get('inputimgsurvey')!=survey.getFirstImage:
                survey.images.remove(survey.getFirstImage)
                survey.images.add(request.POST.get('inputimgsurvey'))
                
            
        
    else:
        usertests = UserTests.objects.get( user_id = request.user.id)
        images = Image.objects.filter( uploader = usertests.id);
        context = {'survey': survey, 'images': images}
        if survey.typesurvey == 'Encuesta':
            return render(request, 'testsforall/edit_encuesta.html', context)    
        if survey.typesurvey == 'Test':
            return render(request, 'testsforall/edit_test.html', context)
        
    
def save_question(request):
    if request.method == "POST":
        post = request.POST
        if post.get('idquestion'):
            question = get_object_or_404(Question, id = post.get('idquestion'))
            question.title = post.get('title')
            if post.get('image'):
                imagequestion = Image(id = post.get('image'))
                question.image = imagequestion
            question.save()
            survey = question.survey
            survey.last_edition = datetime.datetime.now()
            survey.save()
            
        else:
            editedsurvey = get_object_or_404(Survey, id = post.get('surveyid'))
            question = Question(survey = editedsurvey, title = post.get('title'))
            if post.get('image'):
                imagequestion = Image(id = post.get('image'))
                question.image = imagequestion
            question.save()
            survey = question.survey
            survey.last_edition = datetime.datetime.now()
            survey.save()
        
        msg = "se ha guardado correctamente"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    else:
        msg = "No se ha enviado la pregunta de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    
def save_answer(request):
    if request.method == "POST":
        post = request.POST
        if post.get('idanswer'):
            answer = get_object_or_404(Answer, id = post.get('idanswer'))
            answer.title = post.get('title')
            if post.get('image'):
                imageanswer = Image(id = post.get('image'))
                answer.image = imageanswer
            answer.save()
            survey = answer.question.survey
            survey.last_edition = datetime.datetime.now()
            survey.save()
        
        else:
            editedquestion = get_object_or_404(Question, id = post.get('idquestion'))
            answer = Answer(question = editedquestion, title = post.get('title'))
            if post.get('image'):
                imageanswer = Image(id = post.get('image'))
                answer.image = imageanswer
            answer.save()
            survey = answer.question.survey
            survey.last_edition = datetime.datetime.now()
            survey.save()
        
        msg = "se ha guardado correctamente"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    
    else:
        msg = "No se ha enviado la respuesta de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')

def social(request):
    return render(request, 'testsforall/social.html')
        
        
def getFriends(request):
    if request.method == "GET":
        user = User.objects.get(id = request.user.id)
        usertests = UserTests.objects.get(user = user)
        friends = usertests.friends.all()
        resposta = list()
        if friends is not None and friends.count()>0:
            for friend in friends:
                q1 = Q(petitioner = usertests, requested = friend)
                q2 = Q(petitioner = friend, requested = usertests)
                q = q1|q2
                friendrequest = FriendRequest.objects.get(q)
                dateuser = friend.created_at.strftime('%d-%m-%Y')
                datefriends = friendrequest.acceptDate.strftime('%d-%m-%Y')
                resposta.append({
                    'id': friend.id,
                    'username': friend.user.username,
                    'datefriends': datefriends,
                    'dateuser': dateuser,
                });
            
            respostaserialitzada = json.dumps(resposta)
            return HttpResponse(respostaserialitzada, content_type='text/json')
        else:
            resposta = list()
            respostaserialitzada = json.dumps(resposta)
            return HttpResponse(respostaserialitzada, content_type = 'text/json')
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')


def getUsers(request):
    if request.method == "GET":
        usertests = UserTests.objects.get(user__id = request.user.id)
        friendsids = usertests.friends.all().values_list('id', flat = True)
        usersFriendRequest = (UserTests
                             .objects
                             .filter(email_confirmed = True)                #Email confirmado
                             .exclude(solicitante__requested = usertests)   #Usuarios que me han enviado solicitud de amistad
                             .exclude(solicitado__petitioner = usertests)   #Usuarios a los que les he enviado solicitud de amistad
                             .exclude(id = usertests.id)                            #Yo mismo
                             .exclude(id__in = friendsids)                  #Aquellos que ya son amigos mios
                             )
        resposta = list()
        for user in usersFriendRequest:
            created_date = user.created_at.strftime('%d-%m-%Y')
            resposta.append({
            'id': user.id,
            'created_at': created_date,
            'username': user.user.username,
        });
        respostaserialitzada = json.dumps(resposta)
        return HttpResponse(respostaserialitzada, content_type = 'text/json')
        
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')

def sendFriendRequest(request):
    if request.method == "POST":
        petitioner = UserTests.objects.get(user__id = request.user.id)
        requested = UserTests.objects.get(id = request.POST.get('requested'))
        q1 = Q(petitioner = petitioner, requested = requested)
        q2 = Q(petitioner = requested, requested = petitioner)
        q = q1|q2
        tryfriendrequest = FriendRequest.objects.filter(q)
        if not tryfriendrequest:
            friendrequest = FriendRequest.objects.create(petitioner = petitioner, requested = requested)
            friendrequest.save()
            msg = "Enviada solicitud de amistad al usuario "+requested.user.username
            msgjson = list()
            msgjson.append({
                'msg' : msg
            })
            jsonreturn = json.dumps(msgjson)
            return HttpResponse(jsonreturn, content_type='text/json')
        else:
            msg = "La solicitud de amistad ya es existente, si tu no la has enviado comprueba tus solicitudes de amistad"
            msgjson = list()
            msgjson.append({
                'msg' : msg
            })
            jsonreturn = json.dumps(msgjson)
            return HttpResponse(jsonreturn, content_type='text/json')
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
        
def friendRequests(request):
    return render(request, 'testsforall/friendsrequests.html')
    
def getFriendRequests(request):
    if request.method == "GET":
        requestsfriends = FriendRequest.objects.filter(requested__user__id = request.user.id, accepted = False)
        resposta = list()
        for requestfriend in requestsfriends:
            created_date = requestfriend.daterequest.strftime('%d-%m-%Y')
            resposta.append({
            'requestid': requestfriend.id,
            'daterequest': created_date,
            'petitioner': requestfriend.petitioner.user.username,
            'petitionerid': requestfriend.petitioner.id
        });
        respostaserialitzada = json.dumps(resposta)
        return HttpResponse(respostaserialitzada, content_type = 'text/json')
        
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
        
def acceptFriend(request):
    if request.method == "POST":
        
        friendrequest = FriendRequest.objects.get(id = request.POST.get('requestid'))
        friendrequest.accepted = True
        friendrequest.acceptDate = datetime.datetime.now()
        requested = friendrequest.requested
        petitioner = friendrequest.petitioner
        requested.friends.add(petitioner)
        petitioner.friends.add(requested)
        requested.save()
        petitioner.save()
        friendrequest.save()
        msg = "Solicitud de amistad de "+requested.user.username+" aceptada."
        msgjson = list()
        msgjson.append({
            'msg' : msg
        })
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    
def user(request, idUser):
    user = UserTests.objects.get(user__id = idUser)
    context ={
        'user' : user
    }
    return render(request, 'testforall/viewuser.html', context)
    
def createGroup(request):
    return render(request, 'testsforall/creategroup.html')
    
def getMyGroups(request):
    if request.method == "GET":
        usertests = UserTests.objects.get(user__id = request.user.id)
        groups = Group.objects.filter(Q(leader__user__id=request.user.id) |
                           Q(members__user__id=request.user.id)).distinct()
        resposta = list()
        for group in groups:
            created_date = group.created_at.strftime('%d-%m-%Y')
            last_edition = group.last_edition.strftime('%d-%m-%Y')
            resposta.append({
            'userid': usertests.id,
            'name': group.title,
            'created_at': created_date,
            'totalmembers': group.members.all().count(),
            'leader': group.leader.user.username,
            'leade_id': group.leader.id,
            'last_edition': last_edition
        });
        respostaserialitzada = json.dumps(resposta)
        return HttpResponse(respostaserialitzada, content_type = 'text/json')
        
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    return None
    
    
def surveysToDo(request):
    return render(request, 'testsforall/surveystodo.html')
    
def getSurveysToDo(request):
    if request.method == "GET":
        usertests = UserTests.objects.get(user__id = request.user.id)
        q1 = Q(published = True)
        q2 = Q(participants = usertests)
        q = q1|q2
        surveystodo = Survey.objects.filter(q).distinct()
        resposta = list()
        for surveytodo in surveystodo:
            created_at = surveytodo.created_at.strftime('%d-%m-%Y')
            #result = Result.objects.get(user = usertests, survey = surveytodo)
            #score = "No hay resultados"
            #if result is not None and result.score != -1:
            #    score = result.score
            resposta.append({
                'id': surveytodo.id,
                'title': surveytodo.title,
                'typesurvey': surveytodo.typesurvey,
                'created_at': created_at,
                # No implementat'result': score,
                'creator': surveytodo.creator.user.username,
                'creatorid': surveytodo.creator.id
            })
            respostaserialitzada = json.dumps(resposta)
            return HttpResponse(respostaserialitzada, content_type = 'text/json')
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    return None    
    
def solveTest(request):
    if request.method == "POST":
        survey = Survey.objects.get(id = request.POST.get('surveyid'))
        usertests = UserTests.objects.get(user__id = request.user.id)
        answerssended = request.POST.get('answerssended')
        if survey.typesurvey == "minus":
            for answersend in answerssended:
                answer = Answer.objects.get(id = answersend)
                totalpoints = None
                question = Question.objects.get(answer.question)
                if answer.correct:
                    totalpoints = totalpoints+question.value
                else:
                    totalpoints = totalpoints-question.valueminus
            
            result = Result.objects.create(score = totalpoints, user = usertests, survey = survey)
            result.save()
            resposta = list()
            resposta.append({
                    'totalpoints': totalpoints,
                    'title': survey.title,
                })
            respostaserialitzada = json.dumps(resposta)
            return HttpResponse(respostaserialitzada, content_type = 'text/json')
        elif survey.typesurvey == "normal":
            for answersend in answerssended:
                answer = Answer.objects.get(id = answersend)
                totalpoints = None
                question = Question.objects.get(answer.question)
                if answer.correct:
                    totalpoints = totalpoints+question.value
            result = Result.objects.create(score = totalpoints, user = usertests, survey = survey)
            result.save()
            resposta = list()
            resposta.append({
                    'totalpoints': totalpoints,
                    'title': survey.title,
                })
            respostaserialitzada = json.dumps(resposta)
            return HttpResponse(respostaserialitzada, content_type = 'text/json')
    else:
        msg = "No se ha enviado la solicitud de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')