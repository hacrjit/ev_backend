import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = "Your OTP Code"
    message = f"Use the following OTP to verify your account: {otp}"
    send_mail(subject, message, 'youremail@gmail.com', [email])
