#DeepakGuru
#pass-1234

from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from .utils import generate_token, TokenGenerator
from django.views.generic import View
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        
        # Password match validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "authentication/signup.html")
        
        # Check if email already exists
        try:
            if User.objects.get(username=email):
                messages.error(request, "Email already exists.")
                return render(request, "authentication/signup.html")
        except User.DoesNotExist:
            pass  # Email is available

        # Create new user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        # Dynamically generate the domain
        current_site = get_current_site(request)
        email_subject = "Activate Your Account"
        message = render_to_string('activate.html', {
            'user': user,
            'domain': current_site.domain,  # Dynamic domain
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })

        # Send the email
        email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
        email_message.send()

        # Success message
        messages.success(request, "Authentication mail sent successfully. Please check your email.")
        return redirect('login')  # Redirect to login page after successful signup
    
    return render(request, "authentication/signup.html")
class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.success(request,"Account Activated Successfully")
            return redirect('login')
        return render(request,'activatefail.html')


def handlelogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('pass1')

        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if the account is activated
            if user.is_active:
                login(request, user)
                
                # Send login notification email
                send_mail(
                    'Login Notification',
                    'You have successfully logged in.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('home')
            else:
                messages.error(request, "Account is not activated. Please check your email for the activation link.")
                return render(request, "authentication/login.html")
        else:
            messages.warning(request, "Invalid email or password.")
            return render(request, "authentication/login.html")
    else:
        return render(request, "authentication/login.html")



def handlelogout(request):
    logout(request)
    messages.success(request,"successfully logged out.")
    return redirect('/auth/login')