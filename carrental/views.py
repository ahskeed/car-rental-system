# Create your views here.
from _mysql_exceptions import DatabaseError
import json, re
from django.shortcuts import render
from django.db import connection
from django.template import RequestContext
from carrental.models import Model, RentalTransaction, Customer, Car, CarType, Driver
from django.db import transaction
from django.http import HttpResponse


def home(request):
        return render(request, 'home.html')


def view_car_types(request):
    cursor = connection.cursor()
    cursor.execute("select cartype from car_type")
    row = cursor.fetchall()
    row = map(list, row)
    car_type_list = []
    for x in row:
        for y in x:
            car_type_list.append(y)
    context = RequestContext(request, {
        'car_type_list': car_type_list
    })
    cursor.close()
    return render(request, 'view_car_types.html', context)


def view_car_type_details(request, car_type):
    cursor = connection.cursor()
    view = 'view_' + car_type + '.html'
    if car_type == 'top_premium':
        car_type = "'TOP PREMIUM'"
    elif car_type == 'luxury':
        car_type = "'LUXURY AND EXECUTIVE'"
    elif car_type == 'medium':
        car_type = "'MEDIUM'"
    elif car_type == 'budget':
        car_type = "'BUDGET AND ECONOMY'"
    elif car_type == 'suv':
        car_type = "'SUV/MUV'"
    query = "select name from model,car_type where model.car_type_no = car_type.car_type_no and cartype = " + car_type
    cursor.execute(query)
    row = cursor.fetchall()
    row = map(list, row)
    premium_list = []
    for x in row:
        for y in x:
            premium_list.append(y)
    context = RequestContext(request, {
        'premium_list': premium_list
    })
    cursor.close()
    return render(request, view, context)


def model_name_details(request, model_name):
    if model_name == 'merc_eclass':
        name = 'MERCEDES E CLASS'
    elif model_name == 'merc_sclass':
        name = 'MERCEDES S CLASS'
    elif model_name == 'bmw_5':
        name = 'BMW 5 SERIES'
    elif model_name == 'bmw_7':
        name = 'BMW 7 SERIES'

    elif model_name == 'honda_accord':
        name = 'HONDA ACCORD'
    elif model_name == 'toyota_camry':
        name = 'TOYOTA CAMRY'
    elif model_name == 'toyota_corolla':
        name = 'TOYOTA COROLLA'

    elif model_name == 'honda_city':
        name = 'HONDA CITY'
    elif model_name == 'hyundai_verna':
        name = 'HONDA VERNA'
    elif model_name == 'mitsubishi_lancer':
        name = 'MITSUBISHI LANCER'

    elif model_name == 'ambassador':
        name = 'AMBASSADOR'
    elif model_name == 'tata_indigo':
        name = 'TATA INDIGO'
    elif model_name == 'hyundai_accent':
        name = 'HYUNDAI ACCENT'

    elif model_name == 'toyota_cruiser':
        name = 'TOYOTA LAND CRUISER'
    elif model_name == 'tata_safari':
        name = 'TATA MOTORS SAFARI'
    elif model_name == 'toyota_qualis':
        name = 'TOYOTA QUALIS'
    elif model_name == 'innova':
        name = 'INNOVA'

    query = "select * from model where name = '" + name + "'"
    row = Model.objects.raw(query)
    model_list = list(row)
    query = "select model_no from car where cust_uid is null and model_no = " + str(model_list[0].model_no)
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchall()
    if len(list(row)):
        availability = True
    else:
        availability = False

    context = RequestContext(request, {
        'model_name': "/rent/customer_details/"+model_name,
        'model': model_list[0],
        'price': model_list[0].car_type_no.min_price,
        'ac_add': model_list[0].car_type_no.ac_add,
        'deposit': model_list[0].car_type_no.deposit,
        'availability': availability
    })
    cursor.close()
    return render(request, 'model_name_details.html', context)


def customer_details(request, model_name):
    if model_name == 'merc_eclass':
        name = 'MERCEDES E CLASS'
    elif model_name == 'merc_sclass':
        name = 'MERCEDES S CLASS'
    elif model_name == 'bmw_5':
        name = 'BMW 5 SERIES'
    elif model_name == 'bmw_7':
        name = 'BMW 7 SERIES'

    elif model_name == 'honda_accord':
        name = 'HONDA ACCORD'
    elif model_name == 'toyota_camry':
        name = 'TOYOTA CAMRY'
    elif model_name == 'toyota_corolla':
        name = 'TOYOTA COROLLA'

    elif model_name == 'honda_city':
        name = 'HONDA CITY'
    elif model_name == 'hyundai_verna':
        name = 'HONDA VERNA'
    elif model_name == 'mitsubishi_lancer':
        name = 'MITSUBISHI LANCER'

    elif model_name == 'ambassador':
        name = 'AMBASSADOR'
    elif model_name == 'tata_indigo':
        name = 'TATA INDIGO'
    elif model_name == 'hyundai_accent':
        name = 'HYUNDAI ACCENT'

    elif model_name == 'toyota_cruiser':
        name = 'TOYOTA LAND CRUISER'
    elif model_name == 'tata_safari':
        name = 'TATA MOTORS SAFARI'
    elif model_name == 'toyota_qualis':
        name = 'TOYOTA QUALIS'
    elif model_name == 'innova':
        name = 'INNOVA'

    cursor = connection.cursor()
    query = "select place_name from place"
    cursor.execute(query)
    row = cursor.fetchall()
    row = map(list, row)
    place_list = []
    for x in row:
        for y in x:
            place_list.append(y)
    context = RequestContext(request, {
        'place_list': place_list
    })

    if not request.POST:
        return render(request, 'customer_details.html', context)
    else:
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        uid = request.POST.get('uid')
        address = request.POST.get('address')
        primary_phone = request.POST.get('primary_phone')
        license_no = request.POST.get('license_no')
        alt_phone = request.POST.get('alt_phone')
        driver = request.POST.get('driver')
        place = request.POST.get('place')
        no_of_days = request.POST.get('no_of_days')
        ac = request.POST.get('ac')
        error = False
        error_msg = ""
        if not fname or not lname or not uid or not address or not primary_phone or not license_no or not no_of_days:
            error = True
            error_msg = 'Some details are missing. Please fill all fields marked with *.'
        elif len(uid) != 12 or not uid.isdigit():
            error = True
            error_msg = 'Invalid UID!'
        elif len(fname) > 20 or len(lname) > 20:
            error = True
            error_msg = 'First name and Last name should have max. 20 characters each.'
        elif not re.match("^[a-zA-Z]*$", fname) or not re.match("^[a-zA-Z]*$", lname):
            error = True
            error_msg = 'First name and Last name should have only alphabets.'
        elif len(address) > 100:
            error = True
            error_msg = 'Address should not be more than 100 characters.'
        elif len(license_no) > 10:
            error = True
            error_msg = 'License number should not be more than 10 characters.'
        elif len(primary_phone) != 10 or not primary_phone.isdigit():
            error = True
            error_msg = 'Invalid primary phone number.'
        elif alt_phone and (len(alt_phone) != 10 or not alt_phone.isdigit()):
            error = True
            error_msg = 'Invalid alternate phone number.'
        elif not no_of_days.isdigit() or int(no_of_days) > 6 or int(no_of_days) < 1:
            error = True
            error_msg = 'The number of days should be between 1 and 6'
        if error:
            context = RequestContext(request, {
                'place_list': place_list,
                'fname': fname,
                'lname': lname,
                'uid': uid,
                'address': address,
                'primary_phone': primary_phone,
                'license_no': license_no,
                'driver': driver,
                'place': place,
                'ac': ac,
                'no_of_days': no_of_days,
                'error': error,
                'error_msg': error_msg
            })
            return render(request, 'customer_details.html', context)

        no_of_days = int(no_of_days)
        driver_no = []
        if driver:
            query = "select driver_no from driver natural join place where avail = 1 and place_name = '" + place + "'"
            cursor.execute(query)
            row = cursor.fetchone()
            if not row:
                context = RequestContext(request, {
                    'place_list': place_list,
                    'fname': fname,
                    'lname': lname,
                    'uid': uid,
                    'address': address,
                    'primary_phone': primary_phone,
                    'license_no': license_no,
                    'driver': driver,
                    'place': place,
                    'ac': ac,
                    'no_of_days': no_of_days,
                    'error': True,
                    'error_msg': "There are no drivers available for this place."
                })
                return render(request, 'customer_details.html', context)
            driver_no = list(row)

        query = "select * from model where name = '" + name + "'"
        row = Model.objects.raw(query)
        model_list = list(row)
        price = model_list[0].car_type_no.min_price
        deposit = model_list[0].car_type_no.deposit
        car_type_no = str(model_list[0].car_type_no.car_type_no)
        if not ac:
            ac_add = 0
        else:
            ac_add = model_list[0].car_type_no.ac_add

        if ac:
            query = "select license_reg_no, color from car where cust_uid is null and ac = 1 and model_no = " + str(model_list[0].model_no)
        else:
            query = "select license_reg_no, color from car where cust_uid is null and ac = 0 and model_no = " + str(model_list[0].model_no)
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            row = list(row)
            lic_no = row[0]
            color = row[1]
        else:
            context = RequestContext(request, {
                'place_list': place_list,
                'fname': fname,
                'lname': lname,
                'uid': uid,
                'address': address,
                'primary_phone': primary_phone,
                'license_no': license_no,
                'driver': driver,
                'place': place,
                'ac': ac,
                'no_of_days': no_of_days,
                'error': True,
                'error_msg': "No cars with A/c available for this model"
            })
            return render(request, 'customer_details.html', context)
        try:
            cursor = connection.cursor()
            query = "select * from customer where u_id = " + uid
            cursor.execute(query)
            if not cursor.fetchone():
                query = "insert into customer values (" + uid + ",'" + fname + "','" + lname + "','" + address + "','" + license_no + "')"

                cursor.execute(query)

                query = "insert into phone_num(u_id,ph_no) values (" + uid + "," + primary_phone + ")"
                cursor.execute(query)
                if alt_phone:
                    query = "insert into phone_num(u_id,ph_no) values (" + uid + "," + alt_phone + ")"
                    cursor.execute(query)

            query = "update car set cust_uid = " + uid + " where license_reg_no = '" + lic_no + "'"
            cursor.execute(query)

            if driver_no:
                query = "update car set driver_no = " + str(driver_no[0]) + " where license_reg_no = '" + lic_no + "'"
                cursor.execute(query)

            advance = (price + ac_add) * no_of_days + deposit

            query = 'select * from customer where u_id = ' + uid
            uid_obj = list(Customer.objects.raw(query))[0]

            query = "select * from car where license_reg_no = '" + lic_no + "'"
            lic_no_obj = list(Car.objects.raw(query))[0]

            query = 'select * from car_type where car_type_no = ' + car_type_no
            car_type_no_obj = list(CarType.objects.raw(query))[0]
            
            trans = RentalTransaction(u_id=uid_obj, license_reg_no=lic_no_obj, car_type_no=car_type_no_obj, no_of_days=no_of_days, advance=advance)
            if driver_no:
                query = 'select * from driver where driver_no = ' + str(driver_no[0])
                driver_obj = list(Driver.objects.raw(query))[0]
                driver_obj.avail = 0
                driver_obj.save()
                trans.driver_no = driver_obj
            trans.save()
            transaction.commit_unless_managed()
            trans_no = trans.trans_no

            context = RequestContext(request, {
                'success': True,
                'trans_no': trans_no,
                'no_of_days': no_of_days,
                'advance': advance,
                'car_license': lic_no,
                'car_color': color,
                'model_name': name
            })

            return render(request, 'customer_details.html', context)

        except DatabaseError:
            context = RequestContext(request, {
                'error': True,
                'error_msg': "An error occurred during the transaction. Try again later."
            })
            return render(request, 'customer_details.html', context)


def get_details(request, trans_no, uid):
    if not uid.isdigit():
        error_msg = "UID should contain only digits."
        return HttpResponse(json.dumps({
            'status': 'error',
            'msg': error_msg,
            'trans_no': trans_no,
            'uid': uid
        }))
    elif not trans_no.isdigit():
        error_msg = "Booking ID should contain only digits."
        return HttpResponse(json.dumps({
            'status': 'error',
            'msg': error_msg,
            'trans_no': trans_no,
            'uid': uid
        }))
    cursor = connection.cursor()
    query = 'select * from rental_transaction where status = 1 and trans_no = ' + trans_no + ' and u_id = ' + uid
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        error_msg = "No such booking ID or The UID doesn't match the UID provided at the time of booking."
        return HttpResponse(json.dumps({
            'status': 'error',
            'msg': error_msg,
            'trans_no': trans_no,
            'uid': uid
        }))
    trans = list(row)
    query = "select color,name from car,model where car.model_no = model.model_no and license_reg_no = '" + trans[2] + "'"
    cursor.execute(query)
    row = cursor.fetchone()
    row = list(row)

    return HttpResponse(json.dumps({
        'status': 'success',
        'msg': '',
        'trans_no': trans_no,
        'uid': uid,
        'car_license': trans[2],
        'advance': trans[8],
        'no_of_days': trans[10],
        'model_name': row[1],
        'car_color': row[0]
    }))


def cancel_transaction(request):
    if not request.POST:
        return render(request, 'cancel_transaction.html')
    trans_no = request.POST.get('trans_no')
    uid = request.POST.get('uid')
    cursor = connection.cursor()
    query = 'select * from rental_transaction where status = 1 and trans_no = ' + trans_no + ' and u_id = ' + uid
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        error_msg = "No such booking ID or The UID doesn't match the UID provided at the time of booking."
        context = RequestContext(request, {
            'error': True,
            'error_msg': error_msg,
            'trans_no': trans_no,
            'uid': uid
        })
        return render(request, 'cancel_transaction.html', context)
    trans = list(row)
    query = 'update rental_transaction set status = 0 where trans_no = ' + trans_no
    cursor.execute(query)
    query = "update car set cust_uid = null where license_reg_no = '" + trans[2] + "'"
    cursor.execute(query)
    if trans[4]:
        query = "update car set driver_no = null where license_reg_no = '" + trans[2] + "'"
        cursor.execute(query)
        query = "update driver set avail = 1 where driver_no = " + str(trans[4])
        cursor.execute(query)

    transaction.commit_unless_managed()
    context = RequestContext(request, {
        'success': True,
        'trans_no': trans_no,
        'uid': uid
    })
    return render(request, 'cancel_transaction.html', context)