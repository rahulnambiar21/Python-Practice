from django.shortcuts import render
from .models import Contact,User
from django.conf import settings
from django.core.mail import send_mail
import random
def index(request):
	return render(request,'index.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				remarks=request.POST['remarks'],
			)
		msg="Contact Saved Successfully"
		contacts=Contact.objects.all().order_by("-id")[:3]
		return render(request,'contact.html',{'msg':msg,'contacts':contacts})
	else:
		contacts=Contact.objects.all().order_by("-id")[:3]
		return render(request,'contact.html',{'contacts':contacts})

def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registered"
			return render(request,'login.html',{'msg':msg})
		except:
			if request.POST["password"]==request.POST['cpassword']:
				User.objects.create(
					fname=request.POST['fname'],
					lname=request.POST['lname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					address=request.POST['address'],
					password=request.POST['password'],
					profile_picture=request.FILES['profile_picture']
					)
				msg="User Sign Up Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password and Confirmed Password does not Match"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				request.session['email']=user.email
				request.session['fname']=user.fname
				request.session['profile_picture']=user.profile_picture.url
				return render(request,'index.html')
			else:
				msg="Incorrect Password"
				return render(request,'login.html',{'msg':msg})
		except:
			msg="Email not Registered"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_picture']
		msg="User Logged Out Successfully"
		return render(request,'login.html',{'msg':msg})
	except:
		msg="User Logged Out Successfully"
		return render(request,'login.html',{'msg':msg})

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_picture=request.FILES['profile_picture']
		except:
			pass
		user.save()
		msg="Profile Updated Successfully"
		request.session['profile_picture']=user.profile_picture.url
		return render(request,'profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'profile.html',{'user':user})


def change_password(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				if request.POST['old_password']!=request.POST['new_password']:
					user.password=request.POST['new_password']
					user.save()
					del request.session['email']
					del request.session['fname']
					del request.session['profile_picture']
					msg="Password Changed Successfully"
					return render(request,'login.html',{'msg':msg})
				else:
					msg="Old Password and New Password cannot be Same"
					return render(request,'change-password.html',{'msg':msg})
			else:
				msg="New Password and Confirm New Password does not Match"
				return render(request,'change-password.html',{'msg':msg})
		else:
			msg="Old Password does not Match"
			return render(request,'change-password.html',{'msg':msg})
	else:
		return render(request,'change-password.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP for Forgot Passoword'
			message = 'Hello '+user.fname+'Your OTP for Forgot Password is '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			request.session['otp']=otp
			request.session['otp_email']=user.email
			return render(request,'otp.html')

		except:
			msg="Email not Registered"
			return render(request,'forgot-password.html',{'msg':msg})
	else:
		return render(request,'forgot-password.html')

def verify_otp(request):
	otp1=int(request.session['otp'])
	otp2=int(request.POST['otp'])

	if otp1==otp2:
		del request.session['otp']
		return render(request,'new_password.html')
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'msg':msg})

def new_password(request):
	if request.POST['new_password']==request.POST['cnew_password']:
		user=User.objects.get(email=request.session['otp_email'])
		user.password=request.POST['new_password']
		user.save()
		msg="Password Updated Successfully"
		del request.session['otp_email']
		return render(request,'login.html',{'msg':msg})
	else:
		msg="New Password and Confirm New Password does not match"
		return render(request,'new_password.html',{'msg':msg})