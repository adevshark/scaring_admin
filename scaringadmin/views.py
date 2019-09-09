import _thread
import json
import os
import random
import string
import subprocess
import time
from datetime import datetime

from accountkitlogin.views import login_status
from crontab import CronTab
import requests
from django.conf import settings as conf_settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
# ===================================== ADMIN USERS SIGN IN PAGE =========================================
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client

from scaringadmin.models import RPassword, CustomUser, MinedData, SiteList, EmailSettings, TwilioAccountSettings, \
    FacebookAccountKitSettings, Proxy


# Create your views here.
def sign_in(request):
    if request.method == "GET":
        return render(request, 'auth/login.html')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)

        #print(user)

        if not user:
            error_code = 0
            error_message = "No Registered!"
            result = None
        else:
            if user.status == "0":
                error_code = 0
                error_message = "You are blocked"
                result = None
            else:
                verifycode = random_number(6)
                phonenumber = user.phonenumber
                try:
                    to = phonenumber
                    twilio = TwilioAccountSettings.objects.get(id=1)
                    twilio_sid = twilio.twilio_account_sid
                    auth_token = twilio.twilio_auth_token
                    sms_number = twilio.twilio_sms_number
                    client = Client(twilio_sid, auth_token)
                    response = client.messages.create(
                        body=verifycode,
                        to=to, from_=sms_number)
                    error_code = 0
                    error_message = ""
                    result = {
                        "verifycode": verifycode
                    }
                except Exception as e:
                    error_code = 403
                    error_message = e
                    result = None
        response = {
            "error_code": error_code,
            "error_message": error_message,
            "result": result
        }
    return HttpResponse(json.dumps(response), content_type='application/json')


# =================================== phonenumber verify ==========================================
def phonenumberverify(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            if user.status == "0":
                return render(request, 'auth/login.html', {'error': 'You are blocked!'})
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'auth/login.html', {'error': 'User info does not match!'})


# =================================== generate verify code ==========================================
def random_number(length=6):
    """
    Create a random integer with given length.
    For a length of 3 it will be between 100 and 999.
    For a length of 4 it will be between 1000 and 9999.
    """
    return random.randint(10 ** (length - 1), (10 ** (length) - 1))


# ===================================== FORGET PASSWORD RANDOM TOKEN GENERATE ============================
def random_string(str_length=15):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_length))


# =================================== ADMIN FORGET PASSWORD PAGE =========================================
def forgetpassword(request):
    if request.method == "GET":
        return render(request, 'auth/forgetpassword.html')

    if request.method == "POST":
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email)
        if user:
            user = user[0]
            token = random_string()
            RPassword.objects.filter(email=email).delete()
            reset = RPassword(
                email=email,
                token=token
            )
            reset.save()
            subject = 'Reset Password'
            message = ' You need to reset your password.'
            email_from = conf_settings.EMAIL_HOST_USER
            recipient_list = [email, ]

            message = EmailMultiAlternatives(subject, message, email_from, recipient_list)
            html_template = get_template("email/forget_password_email.html").render({
                'username': user.first_name, 'token': token})
            message.attach_alternative(html_template, "text/html")
            message.send()

            return render(request, 'auth/forgetpassword.html', {'success': 'Email Sent!'})
        else:
            return render(request, 'auth/forgetpassword.html', {'error': 'Email does not exist!'})


# =================================== Send Email API ==========================================
@csrf_exempt
def sendEmailApi(request):
    email = request.POST.get("to")
    subject = 'Scraping is ended'
    message = request.POST["message"]
    email_from = conf_settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    html_template = request.POST['html_template']
    try:
        message = EmailMultiAlternatives(subject, message, email_from, recipient_list)
        # html_template = get_template("email/forget_password_email.html").render({
        #     'username': "yy", 'token': "dd"})
        message.attach_alternative(html_template, "text/html")
        message.send()
        error_message = ""
        error_code = 0
    except Exception as e:
        error_code = 403
        error_message = e

    response = {
        'error_message': error_message,
        'error_code': error_code,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


# =================================== Image download api ================================================
@csrf_exempt
def imageDownloadApi(request):
    image_url = request.POST['image_url']
    path = request.POST['image_name']
    try:
        with open(path, 'wb') as handle:
            response = requests.get(image_url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        error_message = ""
        error_code = 0
    except Exception as e:
        error_message = e
        error_code = 403

    response = {
        'error_message': error_message,
        'error_code': error_code,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


# =================================== ADMIN RESET PASSWORD PAGE ==========================================
def admin_password_reset(request, token):
    check_token = RPassword.objects.filter(token=token)
    if check_token:
        email = check_token[0].email
        user = CustomUser.objects.filter(email=email)
        user = user[0]
        return render(request, 'auth/resetpassword.html', {'user': user, 'status': True})
    else:
        return render(request, 'auth/resetpassword.html', {'invalid': True})


# =================================== ADMIN RESET PASSWORD PAGE ==========================================
def admin_password_reset_post(request):
    if request.method == "POST":
        user_id = request.POST.get('id')
        password = request.POST.get('password')
        cpassword = request.POST.get('password1')

        if len(password) < 6:
            return render(request, 'auth/resetpassword.html', {'error': 'Password should be over 6 characters.'})

        if password != cpassword:
            return render(request, 'auth/resetpassword.html', {'error': 'Password does not match.'})

        password = make_password(password)
        user = CustomUser.objects.get(pk=user_id)
        user.password = password
        user.save()

        RPassword.objects.filter(email=user.email).delete()
        return redirect('/signin')


# =================================== SignUp ==========================================
def sign_up(request):
    if request.method == "GET":
        return render(request, 'auth/register.html')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('password1')
        phonenumber = request.POST.get("phonenumber")
        address = request.POST.get("address")

        email_qs = CustomUser.objects.filter(username=email)
        if email_qs.exists():
            return render(request, 'auth/register.html', {'error': 'Email already exist.'})

        if len(password) < 6:
            return render(request, 'auth/register.html', {'error': 'Password should be over 6 characters.'})

        if password != cpassword:
            return render(request, 'auth/register.html', {'error': 'Password does not match.'})

        password = make_password(password)

        user = CustomUser(
            first_name=username,
            username=email,
            email=email,
            password=password,
            phonenumber=phonenumber,
            address=address
        )
        user.save()
        user = authenticate(username=email, password=cpassword)
        login(request, user)
        return HttpResponseRedirect('/')


def addUser(request):
    if request.method == "GET":
        return render(request, 'auth/register.html')

    if request.method == "POST":
        username = request.POST.get("full_name")
        email = request.POST.get('email')
        password = request.POST.get('password')
        phonenumber = request.POST.get("phonenumber")
        address = request.POST.get("address")
        photo = ''

        if request.FILES.get("photo"):
            photo = request.FILES.get("photo")
            fs = FileSystemStorage()
            time = datetime.now().strftime('%Y%m%d%H%M%S')
            filename1 = time + photo.name
            filename_url = fs.save('img/users/' + filename1, photo)
            uploaded_file_url = fs.url(filename_url)
            photo = filename1

        email_qs = CustomUser.objects.filter(username=email)
        if email_qs.exists():
            messages.add_message(request, messages.ERROR, 'Email already exist.')
            return HttpResponseRedirect('/users')
        phonenumber_qs = CustomUser.objects.filter(phonenumber=phonenumber)
        if phonenumber_qs.exists():
            messages.add_message(request, messages.ERROR, 'Phone Number already exist.')
            return HttpResponseRedirect('/users')
        if len(password) < 6:
            messages.add_message(request, messages.ERROR, 'Password should be over 6 characters.')
            return HttpResponseRedirect('/users')

        password = make_password(password)

        try:
            user = CustomUser(
                first_name=username,
                username=email,
                email=email,
                password=password,
                phonenumber=phonenumber,
                address=address,
                photo=photo
            )

            user.save()
            messages.add_message(request, messages.SUCCESS, 'successfully saved.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, e)
        return HttpResponseRedirect('/users')


# ===================================== ADMIN USER EDIT ================================================
def editUser(request):
    userid = request.POST.get("userid")
    username = request.POST.get("full_name")
    email = request.POST.get('email')
    password = request.POST.get('password')
    phonenumber = request.POST.get("phonenumber")
    address = request.POST.get("address")
    photo = ''

    if len(password) < 6:
        messages.add_message(request, messages.ERROR, 'Password should be over 6 characters.')
        return HttpResponseRedirect('/users')

    password = make_password(password)

    if request.FILES.get("photo"):
        photo = request.FILES.get("photo")
        fs = FileSystemStorage()
        time = datetime.now().strftime('%Y%m%d%H%M%S')
        filename1 = time + photo.name
        filename_url = fs.save('img/users/' + filename1, photo)
        uploaded_file_url = fs.url(filename_url)
        photo = filename1

    try:
        user = CustomUser.objects.get(pk=userid)
        user.first_name = username
        user.username = email
        user.email = email
        user.password = password
        user.phonenumber = phonenumber
        user.address = address
        if photo != '':
            user.photo = photo
        user.save()
        messages.add_message(request, messages.SUCCESS, 'successfully edited.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/users')


def deleteUser(request):
    userid = request.POST.get("userid")

    try:
        user = CustomUser.objects.get(pk=int(userid))
        user.delete()
        messages.add_message(request, messages.SUCCESS, 'successfully deleted.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/users')


# ===================================== Block User ================================================
def blockUser(request):
    userid = request.POST.get("block_userid")
    print(userid)
    try:
        user = CustomUser.objects.get(pk=int(userid))
        user.status = "0"
        user.save()
        messages.add_message(request, messages.SUCCESS, 'successfully blocked.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/users')


# ===================================== Block User ================================================
def unBlockUser(request):
    userid = request.POST.get("block_userid")
    print(userid)
    try:
        user = CustomUser.objects.get(pk=int(userid))
        user.status = "1"
        user.save()
        messages.add_message(request, messages.SUCCESS, 'successfully un blocked.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/users')


# ===================================== ADMIN USER GET ================================================
def getUser(request):
    userid = request.GET.get('userid')
    user = CustomUser.objects.get(id=userid)

    response = {
        'first_name': user.first_name,
        'username': user.email,
        'password': user.password,
        'phonenumber': user.phonenumber,
        'address': user.address,
        'photo': user.photo
    }

    return HttpResponse(json.dumps(response), content_type='application/json')


# ===================================== ADMIN USER LOGOUT ================================================
@login_required(login_url='/signin')
def sign_out(request):
    logout(request)
    return HttpResponseRedirect('/signin')


# ===================================== ADMIN DASHBOARD PAGE =============================================
@login_required(login_url='/signin')
def index(request):
    user_count = CustomUser.objects.all().count()

    return render(request, 'dashboard/index.html',
                  # {
                  #     'everyMonthDataNumbers': mindedDatas,
                  #     'eight': eight
                  #  }
                  )


def getEveyMonthData(request):
    this_year = datetime.now().year
    print(this_year)

    one = MinedData.objects.filter(time__year=this_year).filter(month='1').count()
    two = MinedData.objects.filter(time__year=this_year).filter(month='2').count()
    three = MinedData.objects.filter(time__year=this_year).filter(month='3').count()
    four = MinedData.objects.filter(time__year=this_year).filter(month='4').count()
    five = MinedData.objects.filter(time__year=this_year).filter(month='5').count()
    six = MinedData.objects.filter(time__year=this_year).filter(month='6').count()
    seven = MinedData.objects.filter(time__year=this_year).filter(month='7').count()
    eight = MinedData.objects.filter(time__year=this_year).filter(month='8').count()
    nine = MinedData.objects.filter(time__year=this_year).filter(month='9').count()
    ten = MinedData.objects.filter(time__year=this_year).filter(month='10').count()
    eleven = MinedData.objects.filter(time__year=this_year).filter(month='11').count()
    twelve = MinedData.objects.filter(time__year=this_year).filter(month='12').count()

    mindedDatas = [
        one,
        two,
        three,
        four,
        five,
        six,
        seven,
        eight,
        nine,
        ten,
        eleven,
        twelve
    ]

    return HttpResponse(json.dumps(mindedDatas), content_type='application/json')


# @login_required(login_url='/signin')
def userList(request):
    user = request.user
    users = CustomUser.objects.filter(~Q(id=user.id))
    return render(request, 'dashboard/users/users.html', {'users': users})


@login_required(login_url='/signin')
def sites(request):
    sites = SiteList.objects.all()
    return render(request, 'dashboard/sites/sites.html', {"sites": sites})


@login_required(login_url='/signin')
def data(request):
    siteList = SiteList.objects.all()
    return render(request, 'dashboard/data/data.html', {'siteList': siteList})


def getMinedData(request):
    site_id = int(request.POST['site_id'])

    columns = ["id", "title", "description", "image", "price", "currency", "location", "category", "username",
               "phonenumber", "posted_at", "email"]

    if site_id == 0:
        totalData = MinedData.objects.count()
    else:
        totalData = MinedData.objects.filter(site_id=site_id).count()

    totalFieltered = totalData
    limit = int(request.POST.get("length"))
    start = int(request.POST.get("start"))
    order = columns[int(request.POST.get("order[0][column]"))]
    dir = request.POST['order[0][dir]']
    dirr = ""
    if dir == "asc":
        dirr = ""
    else:
        dirr = "-"

    print(limit)

    if request.POST["search[value]"] == "":
        if site_id == 0:
            datas = MinedData.objects.order_by(dirr + order).all()[start:start + limit]
        else:
            datas = MinedData.objects.filter(site_id=site_id).order_by(dirr + order).all()[start:start + limit]
    else:
        search = request.POST["search[value]"]
        if site_id == 0:
            datas = MinedData.objects.filter(title__contains=search).filter(
                ~Q(description=search)).order_by(
                dirr + order).all()[start:start + limit]
            totalFieltered = MinedData.objects.filter(title__contains=search).filter(
                ~Q(description=search)).count()
        else:
            datas = MinedData.objects.filter(site_id=site_id).filter(title__contains=search).filter(
                ~Q(description=search)).order_by(
                dirr + order).all()[start:start + limit]
            totalFieltered = MinedData.objects.filter(site_id=site_id).filter(title__contains=search).filter(
                ~Q(description=search)).count()

    result = []
    if datas:
        for item in datas:
            nestedData = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'image': item.image,
                'price': item.price,
                'currency': item.currency,
                'location': item.location,
                'category': item.category,
                'username': item.username,
                'phonenumber': item.phonenumber,
                'email': item.email,
                'posted_at': item.posted_at,
                'site': item.site,
                'image_name': item.image_name,
                'image_folder': item.image_folder,
            }
            result.append(nestedData)

    response = {
        'draw': int(request.POST['draw']),
        'recordsTotal': int(totalData),
        'recordsFiltered': int(totalFieltered),
        'data': result,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def getMinedDataByID(request):
    id = int(request.POST['id'])
    data = MinedData.objects.get(id=id)
    response = {
        'title': data.title,
        'description': data.description,
        'price': data.price,
        'currency': data.currency,
        'location': data.location,
        'category': data.category,
        'username': data.username,
        'phonenumber': data.phonenumber,
        'email': data.email,
        'view_number': data.view_number,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')


@csrf_exempt
def removeData(request):
    id = int(request.POST['id'])
    try:
        data = MinedData.objects.get(id=id)
        data.delete()
        error_code = 0
        error_message = ""
        result = ""
    except Exception as e:
        error_code = 403
        error_message = e
        result = None

    response = {
        "error_code": error_code,
        "error_message": error_message,
        "result": result
    }
    return HttpResponse(json.dumps(response), content_type='application/json')



@csrf_exempt
def updateMinedData(request):
    id = request.POST['id']
    title = request.POST['title']
    description = request.POST['description']
    price = request.POST['price']
    currency = request.POST['currency']
    location = request.POST['location']
    category = request.POST['category']
    username = request.POST['username']
    phonenumber = request.POST['phonenumber']
    email = request.POST['email']
    # view_number = request.POST['view_number']
    photo = ''
    if request.FILES.getlist('file'):
        uploaded_files = request.FILES.getlist('file')
        fs = FileSystemStorage()

        for item in uploaded_files:
            time = datetime.now().strftime('%Y%m%d%H%M%S')
            filename1 = time + item.name
            filename_url = fs.save('mined/' + filename1, item)
            # filename_url = fs.save('/var/www/vhosts/fijlo.com/mined/' + "avito/" + filename1, item)
            uploaded_file_url = fs.url(filename_url)
            photo += '|' + 'https://fijlo.com/media/mined/' + filename1
            # photo += '|' + 'http://127.0.0.1:8000/media/mined/' + filename1
    photo = photo[1:]
    try:
        data = MinedData.objects.get(id=id)
        data.title = title
        data.description = description
        data.price = price
        data.currency = currency
        data.location = location
        data.category = category
        data.username = username
        data.phonenumber = phonenumber
        data.email = email
        data.image_name = photo
        # data.view_number = view_number
        data.save()
        error_code = 0
        error_message = ""
        result = ""
    except Exception as e:
        error_code = 403
        error_message = e
        result = None

    response = {
        "error_code": error_code,
        "error_message": error_message,
        "result": result
    }
    return HttpResponse(json.dumps(response), content_type='application/json')





@login_required(login_url='/signin')
def scarpingSettings(request):
    return render(request, 'dashboard/settings/proxySettings.html')


@login_required(login_url='/signin')
def apiSettings(request):
    return render(request, 'dashboard/settings/apiSettings.html')


@login_required(login_url='/signin')
def emailSettings(request):
    setting_email = EmailSettings.objects.first()
    return render(request, 'dashboard/settings/emailSettings.html', {"setting_email": setting_email})


def addSite(request):
    site_name = request.POST["site_name"]
    site_url = request.POST["site_url"]
    directory_name = request.POST["directory_name"]
    cron_time = request.POST["cron_time"]

    directory = "/var/www/vhosts/fijlo.com/data/" + directory_name

    if not os.path.exists(directory):
        os.mkdir(directory)
        messages.add_message(request, messages.SUCCESS, directory_name + 'is created.')

    siteList = SiteList(
        site_name=site_name,
        site_url=site_url,
        directory_name=directory_name,
        cron_time=cron_time
    )
    siteList.save()
    return HttpResponseRedirect('/sites')


def getSite(request):
    site_id = request.GET.get('siteid')
    site = SiteList.objects.get(id=site_id)

    response = {
        'site_name': site.site_name,
        'site_url': site.site_url,
        'directory_name': site.directory_name,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')


# ===================================== Site EDIT ================================================
def editSite(request):
    site_id = request.POST['siteid']
    site_name = request.POST.get("site_name")
    site_url = request.POST.get("site_url")
    directory_name = request.POST["directory_name"]
    cron_time = request.POST["cron_time"]

    try:
        directory = "/var/www/vhosts/fijlo.com/data/" + directory_name
        if not os.path.exists(directory):
            os.mkdir(directory)

        site = SiteList.objects.get(pk=site_id)
        site.site_name = site_name
        site.site_url = site_url
        site.directory_name = directory_name
        site.cron_time = cron_time
        site.save()
        messages.add_message(request, messages.SUCCESS, 'successfully edited.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/sites')


# =====================================  UpdateCronJobStatus ================================================
def updateCronJobStatus(request):
    site_id = request.POST['siteid']
    cron_status = request.POST["cron_status"]
    site = SiteList.objects.get(id=site_id)
    site_url = site.site_url

    my_cron = CronTab("www-data")

    avito = "https://www.avito.ma"
    tayara = "https://www.tayara.tn"
    ouedkniss = "https://www.ouedkniss.com"

    cron_time = site.cron_time

    try:
        site = SiteList.objects.get(pk=site_id)
        site.cron_status = cron_status
        site.save()
        messages.add_message(request, messages.SUCCESS, 'successfully updated.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
    if cron_status == "Start":
        # cmd1 = 'sh ~/avito/avito/spiders/bash.sh'
        # os.system(cmd1)
        print(my_cron)

        if avito in site_url:
            # for job in my_cron:
            print("avito")
            job = my_cron.new(command="/usr/local/bin/scrapy runspider '/var/www/vhosts/fijlo.com/crawler/avito/spiders/avito_spider.py'",
                              comment=avito)
            job.minute.on(cron_time.minute)
            job.hour.on(cron_time.hour)
            # job.hour.every(1)
            my_cron.write()
        if ouedkniss in site_url:
            # for job in my_cron:
            print("ouekniss")
            job = my_cron.new(command="cd /var/www/vhosts/fijlo.com/crawler/avito/ ; /usr/local/bin/scrapy runspider 'spiders/ouedkniss_spider.py'",
                              comment=ouedkniss)
            job.minute.on(cron_time.minute)
            job.hour.on(cron_time.hour)
            # job.hour.every(1)
            my_cron.write()
        if tayara in site_url:
            # for job in my_cron:
            print("tayara")
            job = my_cron.new(command="/usr/local/bin/scrapy runspider '/var/www/vhosts/fijlo.com/crawler/avito/spiders/tayara_spider.py'",
                              comment=tayara)
            job.minute.on(cron_time.minute)
            job.hour.on(cron_time.hour)
            # job.hour.every(1)
            my_cron.write()

    if cron_status == "Stop" or cron_status == "Pause":
        if avito in site_url:
            for job in my_cron:
                if job.comment == avito:
                    my_cron.remove(job)
                    my_cron.write()
        if ouedkniss in site_url:
            for job in my_cron:
                if job.comment == ouedkniss:
                    my_cron.remove(job)
                    my_cron.write()

        if tayara in site_url:
            for job in my_cron:
                if job.comment == tayara:
                    my_cron.remove(job)
                    my_cron.write()

        if cron_status == "Stop":
            site.scraped_status = "Stop"
            site.save()
        if cron_status == "Pause":
            site.scraped_status = "Pause"
            site.save()

    if cron_status == "Start":
        site.scraped_status = "Start"
        site.save()

        for aa in my_cron:
            print(aa)
    return HttpResponseRedirect('/sites')


# ===================================== Site Delete ================================================
def deleteSite(request):
    site_id = request.POST.get("siteid")

    try:
        user = SiteList.objects.get(pk=int(site_id))
        directory_name = user.directory_name
        directory = "media/scraped_imgs/" + directory_name
        # if os.path.exists(directory):
        #     os.removedirs(directory)

        user.delete()
        messages.add_message(request, messages.SUCCESS, 'successfully deleted.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/sites')


# ===================================== Email Setting ================================================
def update_email_setting(request):
    smtp_port = request.POST["smtp_port"]
    smtp_host = request.POST["smtp_host"]
    smtp_email = request.POST["smtp_email"]
    smtp_password = request.POST["smtp_password"]
    smtp_id = request.POST["smtp_id"]
    emailSetting = EmailSettings.objects.get(id=smtp_id)
    emailSetting.smtp_port = smtp_port
    emailSetting.smtp_host = smtp_host
    emailSetting.smtp_email = smtp_email
    emailSetting.smtp_password = smtp_password
    emailSetting.save()
    return HttpResponseRedirect('/emailSettings')


def update_admin_email(request):
    admin_email = request.POST['admin_email']
    smtp_id = request.POST["smtp_id"]
    adminEmailSetting = EmailSettings.objects.get(id=smtp_id)
    adminEmailSetting.admin_email = admin_email
    adminEmailSetting.save()
    return HttpResponseRedirect('/emailSettings')

# ===================================== twilio Settings ================================================
@login_required(login_url='/signin')
def smsSettings(request):
    twilio = TwilioAccountSettings.objects.first()
    fb = FacebookAccountKitSettings.objects.first()
    return render(request, 'dashboard/settings/smsSettings.html', {"twilio": twilio, "fb": fb})


def updateTwilio(request):
    sid = request.POST["twilio_sid"]
    auth_token = request.POST["twilio_auth_token"]
    sms_number = request.POST["twilio_sms_number"]
    id = request.POST["id"]
    twilio = TwilioAccountSettings.objects.get(id=id)
    twilio.twilio_account_sid = sid
    twilio.twilio_auth_token = auth_token
    twilio.twilio_sms_number = sms_number
    twilio.save()
    return HttpResponseRedirect("/smsSettings")


def updateFacebookAccountKit(request):
    fb_app_id = request.POST["fb_app_id"]
    fb_secret_id = request.POST["fb_secret_id"]
    id = request.POST['id']
    fb = FacebookAccountKitSettings.objects.get(id=id)
    fb.fb_app_id = fb_app_id
    fb.fb_secret_id = fb_secret_id
    fb.save()
    return HttpResponseRedirect("/smsSettings")


# ===================================== Edit Actual LoggedIn User ================================================
def user_profile(request):
    user = request.user
    return render(request, 'auth/edit_profile.html', {"user": user})


def edit_user_profile(request):
    userid = request.POST.get("userid")
    username = request.POST.get("full_name")
    email = request.POST.get('email')
    password = request.POST.get('password')
    cpassword = request.POST['cpassword']
    phonenumber = request.POST.get("phonenumber")
    address = request.POST.get("address")
    photo = ''

    if len(password) < 6:
        messages.add_message(request, messages.ERROR, 'Password should be over 6 characters.')
        return HttpResponseRedirect('/user_profile')

    if password != cpassword:
        messages.add_message(request, messages.ERROR, 'Password does not match.')
        return HttpResponseRedirect('/user_profile')

    ecrypted_password = make_password(password)
    if request.FILES.get("photo"):
        photo = request.FILES.get("photo")
        fs = FileSystemStorage()
        time = datetime.now().strftime('%Y%m%d%H%M%S')
        filename1 = time + photo.name
        filename_url = fs.save('img/users/' + filename1, photo)
        uploaded_file_url = fs.url(filename_url)
        photo = filename1

    try:
        user = CustomUser.objects.get(pk=userid)
        user.first_name = username
        user.username = email
        user.email = email
        user.password = ecrypted_password
        user.phonenumber = phonenumber
        user.address = address
        if photo != '':
            user.photo = photo
        user.save()

        me = authenticate(username=email, password=password)
        login(request, me)

        messages.add_message(request, messages.SUCCESS, 'successfully edited.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)

    return HttpResponseRedirect('/user_profile')


# ===================================== Proxy Setting ================================================
@login_required(login_url='/signin')
def proxySettings(request):
    proxies = Proxy.objects.all()
    return render(request, 'dashboard/settings/proxySettings.html', {"proxies": proxies})


def addProxy(request):
    username = request.POST['username']
    password = request.POST['password']
    ip = request.POST['ip']

    try:
        proxy = Proxy(
            username=username,
            password=password,
            ip=ip
        )
        proxy.save()
        messages.add_message(request, messages.SUCCESS, 'successfully added.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
    return HttpResponseRedirect('/proxySettings')


def deleteProxy(request):
    proxy_id = request.POST['proxy_id']
    try:
        proxy = Proxy.objects.filter(id=proxy_id)
        proxy.delete()
        messages.add_message(request, messages.SUCCESS, 'successfully deleted.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
    return HttpResponseRedirect('/proxySettings')


def setProxy(request):
    data_proxies = Proxy.objects.all()
    try:
        with open("/var/www/vhosts/fijlo.com/crawler/proxy.txt", mode="a", encoding='utf-8') as proxies:
            proxies.truncate(0)
            for item in data_proxies:
                line = item.username+":"+item.password+"@"+item.ip
                proxies.write(line + '\n')
            proxies.close()
        messages.add_message(request, messages.SUCCESS, 'successfully proxy set.')
    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
    return HttpResponseRedirect('/proxySettings')


@csrf_exempt
def success_page(request):
    context = login_status(request)
    return HttpResponseRedirect("/")

def accountKit(request):
    return render(request, 'auth/accountKit.html')
