from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.message import EmailMessage
from tokenize import generate_tokens
from click import password_option
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login, logout
from gfg import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from .tokens import generate_token

# Create your views here.

def home(request):
    return render(request, "authentication/index.html")
    # return HttpResponse("hello, children")

def signup(request):
    
    if request.method == "POST":
        
        # username = request.POST.get("username")
        # fname = request.POST.get("fname")
        # lname = request.POST.get("lname")
        # email = request.POST("email")
        # pass1 = request.POST("pass1")
        # pass2 = request.POST("pass2")
        
        username = request.POST["username"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)<5:
            messages.error(request, "Username must be under 20 charcters!!")
            # return redirect('home')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        
        myuser.save() 
        messages.success(request, "Your have succeded in creating an account! we have sent you a confirmation email. confirm email to activate account")
        
        # welcome email
        subject = " welcome to StudentKonnect"
        message = " Hello " + myuser.first_name + "!! \n" + "Welcome to student connect \n Thank you for visiting our website \n check your email for confirmation to activate your account.  \n\n Thank you"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        
        # confirmmail
        current_site = get_current_site(request)
        email_subject = "confirm your email @ studentcokkect"
        message2 = render_to_string('email_confrimation.html'),{
            'name': myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_b64encode(force_bytes(myuser.pk)),
            'token' : generate_tokens.make_token(myuser)
        }
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()
        
        return redirect("signin")
    
    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html",{'fname': fname})
        
            
        else:
            messages.error(request, "bad condition")
            return redirect('home')
    
    
    return render(request, "authentication/signin.html")

def signout(request):
    # pass
    logout(request)
    messages.success(request, "logged out succesfully")
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None
