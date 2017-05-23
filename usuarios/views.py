# encoding: utf-8
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit
from .forms import LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from testsforall.models import UserTests
from django.core.mail import send_mail, BadHeaderError, EmailMessage, EmailMultiAlternatives
from django.utils.html import strip_tags
import json, os
from django.template.loader import render_to_string
from django.conf import settings
from email.MIMEImage import MIMEImage




def views_signin(request):
    if request.method=='POST':
        form=LoginForm( request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            seguent = request.GET.get('next', default=None)
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if bool( seguent ):
                        return HttpResponseRedirect (seguent)
                    else:
                        return HttpResponseRedirect (reverse('testsforall:miCuenta'))
                else:
                    messages.error(request, 'Error, usuario inactivo.')
            else:
                messages.error(request, 'Error, usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
        
    form.helper = FormHelper()
    form.helper.form_class = 'blueForms'
    form.helper.label_class = 'col-lg-2'
    form.helper.field_class = 'col-lg-10'
    form.helper.add_input(Submit('submit', 'Entrar'))
    return render(request, 'signin.html', {'form':form, 'pagetitle' : 'Login', 'titulo' : 'Login',})
    


def views_signup(request):
    if request.method == 'POST':
        post = request.POST
        username = post.get('username')
        email = post.get('email')
        password = post.get('password')
        newuser = User.objects.create_user(username, email, password)
        newusertests = UserTests.objects.create(user = newuser)
        send_email(request, email, newusertests)
        return HttpResponseRedirect(reverse('testsforall:checkmail'))
        
    else:
        return render(request, 'signup.html')



def send_email(request, mail, user):
    subject = "Bienvenido a tests4all"
    html_content = render_to_string('welcomemail.html', {'hashlink': user.hashlink[0:10], 'user': user})
    text_content = strip_tags(html_content)
    from_email = "tests4allnoreply@gmail.com"
    msg = EmailMultiAlternatives(subject, text_content, from_email, [mail])
    
    for f in ['logo.png']:
        fp = open(os.path.join(settings.BASE_DIR, 'img/'+f), 'rb')
        msg_img = MIMEImage(fp.read())
        fp.close()
        msg_img.add_header('Content-ID', '<{}>'.format(f))
        msg.attach(msg_img)

    
    
    msg.attach_alternative(html_content, "text/html")
    msg.send()

        
def views_checkuser(request):
    if request.method == 'POST':
        checkusername = request.POST.get('username')
        userexists = User.objects.filter(username__exact = checkusername).count()>0
        checkjson = list();
        checkjson.append({
            'userexists' : userexists
        });
        jsonreturn = json.dumps(checkjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    else:
        msg = "No se ha enviado la respuesta de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
        
        
def views_checkmail(request):
    if request.method == 'POST':
        checkmail = request.POST.get('mail')
        mailexists = User.objects.filter(email = checkmail).count()>0
        checkjson = list();
        checkjson.append({
            'mailexists' : mailexists
        });
        jsonreturn = json.dumps(checkjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    else:
        msg = "No se ha enviado la respuesta de forma correcta"
        msgjson = list();
        msgjson.append({
            'msg' : msg
        });
        jsonreturn = json.dumps(msgjson)
        return HttpResponse(jsonreturn, content_type='text/json')
    
    
def views_confirmmail(request, hashlink, userid):
    user = UserTests.objects.get(id = userid);
    if user.hashlink == hashlink:
        user.email_confirmed = True
        user.save()
        return render(request, 'welcome.html', )
    else:
        return render(request, 'badattempt.html', {'hashlinkmail':hashlink, 'userhashlink':user.hashlink, 'user': user.user.username})