# Create your views here.
from _mysql_exceptions import DatabaseError
from django.shortcuts import render
from django.db import connection
from django.template import RequestContext
from carrental.models import Model, RentalTransaction, Customer, Car, CarType, Driver
from django.db import  transaction


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
        no_of_days = int(request.POST.get('no_of_days'))
        ac = request.POST.get('ac')
        error = False
        error_msg = ""
        if not fname or not lname or not uid or not address or not primary_phone or not license_no or not no_of_days:
            error = True
            error_msg = 'Some details are missing. Please fill all fields marked with *.'
        elif len(uid) > 13:
            error = True
            error_msg = 'Invalid UID!'
        elif len(fname) > 20 or len(lname) > 20:
            error = True
            error_msg = 'First name and Last name should have max. 20 characters each.'
        elif len(address) > 100:
            error = True
            error_msg = 'Address should not be more than 100 characters.'
        elif len(license_no) > 10:
            error = True
            error_msg = 'License number should not be more than 10 characters.'
        elif len(primary_phone) != 10:
            error = True
            error_msg = 'Invalid primary phone number.'
        elif alt_phone and len(alt_phone) != 10:
            error = True
            error_msg = 'Invalid alternate phone number.'
        elif no_of_days > 6 or no_of_days < 1:
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
                'ac': ac,
                'no_of_days': no_of_days,
                'error': error,
                'error_msg': error_msg
            })
            return render(request, 'customer_details.html', context)

        driver_no = []
        if driver:
            query = "select driver_no from driver natural join place where avail = 1 and place_name = '" + place + "'"
            cursor.execute(query)
            row = cursor.fetchone()
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
            query = "select license_reg_no from car where cust_uid is null and ac = 1 and model_no = " + str(model_list[0].model_no)
        else:
            query = "select license_reg_no from car where cust_uid is null and model_no = " + str(model_list[0].model_no)
        cursor.execute(query)
        lic_no = cursor.fetchone()
        if lic_no:
            lic_no = list(lic_no)[0]
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
                'ac': ac,
                'no_of_days': no_of_days,
                'error': True,
                'error_msg': "No cars with A/c available for this model"
            })
            return render(request, 'customer_details.html', context)
        try:
            query = "insert into customer values (" + uid + ",'" + fname + "','" + lname + "','" + address + "','" + license_no + "')"
            cursor = connection.cursor()
            cursor.execute(query)

            query = "insert into phone_num(u_id,ph_no) values (" + uid + "," + primary_phone + ")"
            cursor.execute(query)
            if alt_phone:
                query = "insert into phone_num(u_id,ph_no) values (" + uid + "," + alt_phone + ")"
                cursor.execute(query)

            query = "update car set cust_uid = " + uid + " where license_reg_no = '" + lic_no + "'"
            print query
            cursor.execute(query)

            if driver_no:
                query = "update car set driver_no = " + str(driver_no[0]) + " where license_reg_no = '" + lic_no + "'"
                cursor.execute(query)

            advance = (price + ac_add) * no_of_days + deposit

            #
            # if driver_no:
            #     query = "insert into rental_transaction (u_id,license_reg_no,car_type_no,driver_no,no_of_days,advance)" \
            #         " values (" + uid + ",'" + lic_no + "'," + car_type_no + "," + str(driver_no[0]) + "," + no_of_days + "," + advance + ")"
            # else:
            #     query = "insert into rental_transaction (u_id,license_reg_no,car_type_no,no_of_days,advance)" \
            #         " values (" + uid + ",'" + lic_no + "'," + car_type_no + "," + no_of_days + "," + advance + ")"
            #
            #
            # cursor.execute(query)

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
            
            print lic_no
            print trans_no

            context = RequestContext(request, {
                'success': True,
                'trans_no': trans_no,
                'no_of_days': no_of_days,
                'advance': advance,
                'car_license': lic_no,
                'model_name': name
            })

            return render(request, 'customer_details.html', context)

        except DatabaseError:
            context = RequestContext(request, {
                'error': True,
                'error_msg': "An error occurred during the transaction. Try again later."
            })
            return render(request, 'customer_details.html', context)






