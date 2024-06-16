from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Courier,Branch,Tracker,User,Report
from django.db.models import Q
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Courierform
from .models import ContactMessage
def home(request):
     if request.method == 'POST':
        sam=ContactMessage()
        sam.name1=request.POST['first']
        sam.email=request.POST['second']
        sam.message=request.POST['third']
        sam.save()
        return redirect('home') 
     else:
        sam = None 
        return render(request, 'home.html',{'sam':sam})

@login_required(login_url='login')
def courier_registration(request):
    if request.method == 'POST':
            form = Courierform()
            form.namee=request.POST['namee']
            form.contactPhone=request.POST['contactPhone']
            form.pickupAddress=request.POST['pickupAddress']
            form.sender_email=request.POST['senderEmail']
            form.emergencyContactName=request.POST['emergencyContactName']
            form.emergencyContactPhone=request.POST['emergencyContactPhone']
            form.receiver_email=request.POST['receiverEmail']
            form.deliveryAddress=request.POST['deliveryAddress']
            form.pickupTime=request.POST['pickupTime']
            form.ampm=request.POST['ampm']
            form.packageSize=request.POST['packageSize']
            form.packageCategory=request.POST['packageCategory']
            form.packageWeight=request.POST['packageWeight']
            form.serviceType=request.POST['serviceType']
            form.privacyPolicyAgreement=bool(request.POST.get('privacyPolicyAgreement'))
            form.termsAgreement=bool(request.POST.get('termsAgreement'))
            form.save()  
            return render(request,"sucessp.html") 
    else:
        form = None 
    return render(request, 'booking.html', {'form': form})


def login_user(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        try:
            user=User.objects.get(email=email)
        except:
            return render(request,"login.html",{"error":"Check Email!"})
        if user.check_password(password):
            login(request,user)
            if user.manager is False and user.worker is False:
                return redirect('track')
            elif user.worker is True:
                return redirect('shipments')
            else:
                return redirect('dashboard')
    return render(request,"login.html")


def logout_user(request):
    logout(request)
    return redirect('login')
def signup(request):
    if request.method=="POST":
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        try:
            user=User.objects.create_user(username=username,email=email,password=password)
            login(request,user)
            return redirect('login')
        except:
            return render(request,'signup.html',{'error':'Change email or username'})

    return render(request,'signup.html')



@login_required(login_url='login')
def manager(request):
    if request.user.manager==True:
        branch=Branch.objects.get(manager=request.user)
        courier_all=branch.couriers.all().order_by('-created')
        pending=courier_all.filter(status='pending')
        courier_all=courier_all.filter(status='Delivered')
        if request.method=="POST":
            client_id=request.POST.get("client_id")
            try:
                courier=Courier.objects.get(courier_id=client_id)
            except:
                return render(request,'dashboard.html',{'couriers':courier_all,'error':"something went to wrong"})
            if courier is not None:
                Tracker.objects.filter(courier=courier).update(present=branch)
                if courier.status=="In Transit" or courier.status=="pending":
                    courier.status="pending"
                    courier.save()
                    branch.couriers.add(courier)
                else:
                    return render(request,'dashboard.html',{'couriers':courier_all,'error':"already delivered"})
            
        return render(request,'dashboard.html',{'couriers':courier_all,'branch':branch,'todays':pending})
    else:
        return HttpResponse("Not allowed")


@login_required(login_url='login')
def deliveryboy(request):
    try:
        branch=Branch.objects.filter(delivery=request.user)[0]
        couriers=Branch.objects.get(name=branch)
        couriers=couriers.couriers.filter(status="pending")
    except:
        couriers={}
    if request.method=="POST":
        client_id=request.POST.get("client_id")
        try:
            courier=Courier.objects.get(courier_id=client_id)
        except:
            return render(request,'shipments.html',{'couriers':couriers,'error':"Courier does not exist!!"})
        if courier is not None:
            courier.status="Delivered"
            courier.delivery_by=request.user.username
            courier.save()
    return render(request,'shipments.html',{'couriers':couriers})



@login_required(login_url='login')
def customer(request):
    if request.method=="POST":
        id=request.POST.get("tracking-number")
        try:
            tracker=Tracker.objects.get(courier__courier_id=id)
        except:
            return render(request,'track.html',{'error':'Check id!'})
        
        if request.user.id == tracker.courier.customer.id:
            return render(request,'track.html',{'tracker':tracker})
        else:
            return render(request,'track.html',{'error':'Not Allowed!'})
    return render(request,'track.html')


@login_required(login_url='login')
def hire_deliveryboy(request):
    branch=Branch.objects.get(manager=request.user)
    deliveryboys=branch.delivery.all()
    if request.method=="POST":
        email=request.POST.get("deliveryboy_email")
        try:
            user=User.objects.get(email=email.lower())
            try:
                newboy=branch.delivery.get(id=user.id)
                branch.delivery.remove(newboy)
            except:
                branchs=Branch.objects.filter(delivery=user)
                user.worker=True
                user.save()
                if len(branchs) !=0:
                    branchs[0].delivery.remove(user)
                branch.delivery.add(user)
            return render(request,'hiring_delivaryboy.html',{'deliveryboys':deliveryboys,'branch':branch})
        except:
            return render(request,'hiring_delivaryboy.html',{'deliveryboys':deliveryboys,'branch':branch,'error':"user not exist"})
    return render(request,'hiring_delivaryboy.html',{'deliveryboys':deliveryboys,'branch':branch})


@login_required(login_url='login')
def view_reports(request):
    branch=Branch.objects.get(manager=request.user)
    reports=branch.reports.all()
    return render(request,'report.html',{'reports':reports})



"""@login_required(login_url='login')
def create_reports(request,id):
    try:
        courier=Courier.objects.get(courier_id=id)
    except:
        return render(request,'create_report.html',{'error':'something went to wrong'})
    if request.method=="POST":
        report_text=request.POST.get('report-body')
        branch=Tracker.objects.get(courier=courier)
        report=Report.objects.create(report=report_text,courier=courier,customer=request.user)
        branch.present.reports.add(report)
        
    return render(request,'create_report.html',{'courier':courier})"""

@login_required(login_url='login')
def create_reports(request, id):
    try:
        courier = Courier.objects.get(courier_id=id)
    except Courier.DoesNotExist:
        return render(request, 'create_report.html', {'error': 'Courier not found'})

    if request.method == "POST":
        report_text = request.POST.get('report-body')

        try:
            branch = Tracker.objects.get(courier=courier)
        except Tracker.DoesNotExist:
            return render(request, 'create_report.html', {'error': 'Tracker not found'})
        if branch.present:
            report = Report.objects.create(report=report_text, courier=courier, customer=request.user)
            branch.present.reports.add(report)
            return render(request, 'create_report.html', {'courier': courier, 'success': 'Report added successfully'})
        else:
            return render(request, 'create_report.html', {'courier': courier, 'error': 'Branch is None'})
    
    return render(request, 'create_report.html', {'courier': courier})





def login_userr(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        try:
            user=User.objects.get(email=email)
        except:
            return render(request,"login.html",{"error":"Check Email!"})
        if user.check_password(password):
            login(request,user)
            if user.manager is False and user.worker is False:
                return redirect('booking')
            elif user.worker is True:
                return redirect('shipments')
            else:
                return redirect('dashboard')
    return render(request,"login.html")


