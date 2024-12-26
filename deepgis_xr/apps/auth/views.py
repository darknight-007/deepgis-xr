import os
from datetime import datetime, timedelta
import random
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views.generic import View
from twilio.rest import Client
from .models import User, VerificationCode
from .forms import PhoneLoginForm, VerificationForm

# Initialize Twilio client
twilio_client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN
)

# Test phone number for development
TEST_PHONE_NUMBER = '+12345678900'

def generate_verification_code():
    """Generate a random 6-digit code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

class PhoneLoginView(View):
    template_name = 'auth/phone_login.html'
    
    def get(self, request):
        form = PhoneLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={'username': str(phone_number)}
            )
            
            # Special handling for test phone number
            if str(phone_number) == TEST_PHONE_NUMBER:
                user.is_phone_verified = True
                user.save()
                login(request, user)
                return redirect('index')
            
            # Generate verification code
            code = generate_verification_code()
            expires_at = datetime.now() + timedelta(minutes=10)
            
            VerificationCode.objects.create(
                user=user,
                code=code,
                expires_at=expires_at
            )
            
            # Send SMS via Twilio
            try:
                message = twilio_client.messages.create(
                    body=f'Your DeepGIS verification code is: {code}',
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=str(phone_number)
                )
                
                # Store user ID in session for verification
                request.session['phone_auth_user_id'] = user.id
                return redirect('verify_code')
                
            except Exception as e:
                form.add_error(None, f"Error sending verification code: {str(e)}")
        
        return render(request, self.template_name, {'form': form})

class VerifyCodeView(View):
    template_name = 'auth/verify_code.html'
    
    def get(self, request):
        if 'phone_auth_user_id' not in request.session:
            return redirect('phone_login')
            
        form = VerificationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if 'phone_auth_user_id' not in request.session:
            return redirect('phone_login')
            
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user_id = request.session['phone_auth_user_id']
            
            try:
                user = User.objects.get(id=user_id)
                verification = VerificationCode.objects.filter(
                    user=user,
                    code=code,
                    is_used=False,
                    expires_at__gt=datetime.now()
                ).latest('created_at')
                
                # Mark code as used
                verification.is_used = True
                verification.save()
                
                # Mark user as verified and login
                user.is_phone_verified = True
                user.save()
                login(request, user)
                
                # Clean up session
                del request.session['phone_auth_user_id']
                
                return redirect('index')
                
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                form.add_error(None, "Invalid or expired verification code")
        
        return render(request, self.template_name, {'form': form}) 