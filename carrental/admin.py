from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection, transaction, IntegrityError
from django.template import RequestContext
import json,re

SALARY_PER_DAY = 1500


def home(request):
    return render(request, 'admin_home.html')


def pay_driver(request):
    if not request.POST:
        return render(request, 'admin_pay_driver.html')
    driver_no = request.POST.get('driver_no')
    if not driver_no:
        context = RequestContext(request, {
            'driver_no': driver_no,
            'error': True,
            'error_msg': 'Please enter driver number.'
        })
        return render(request, 'admin_pay_driver.html', context)
    if not driver_no.isdigit():
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Driver number should contain only digits.',
            'driver_no': driver_no
        })
        return render(request, 'admin_pay_driver.html', context)
    elif not len(driver_no) > 20:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Driver number should contain max. 20 digits.',
            'driver_no': driver_no
        })
        return render(request, 'admin_pay_driver.html', context)
    cursor = connection.cursor()
    query = 'select salary from driver where driver_no = ' + driver_no
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        context = RequestContext(request, {
            'driver_no': driver_no,
            'error': True,
            'error_msg': 'No such driver exists.'
        })
        return render(request, 'admin_pay_driver.html', context)
    salary = list(row)[0] or 0
    query = 'update driver set total_days = 0 where driver_no = ' + driver_no
    cursor.execute(query)
    query = 'update driver set salary = 0 where driver_no = ' + driver_no
    cursor.execute(query)
    transaction.commit_unless_managed()

    context = RequestContext(request, {
        'driver_no': driver_no,
        'salary': salary,
        'success': True
    })
    return render(request, 'admin_pay_driver.html', context)


def get_driver_details(request, driver_no):
    if not driver_no.isdigit():
        return HttpResponse(json.dumps({
            'error': True,
            'error_msg': 'Driver number should contain only digits.',
            'driver_no': driver_no
        }))
    elif not len(driver_no) > 20:
        return HttpResponse(json.dumps({
            'error': True,
            'error_msg': 'Driver number should contain max. 20 digits.',
            'driver_no': driver_no
        }))
    cursor = connection.cursor()
    query = 'select * from driver natural join place where driver_no = ' + driver_no
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        data = {
            'error': True,
            'error_msg': 'No such driver exists.',
            'driver_no': driver_no
        }
        return HttpResponse(json.dumps(data))
    row = list(row)
    data = {
        'driver_no': driver_no,
        'uid': row[2],
        'name': row[3],
        'ph_num': row[4],
        'total_days': row[5],
        'salary': row[6],
        'place': row[8]
    }
    return HttpResponse(json.dumps(data))


def rent(request):
    if not request.POST:
        return render(request, 'admin_rent.html')
    trans_no = request.POST.get('trans_no')
    cursor = connection.cursor()
    query = 'select time_rent from rental_transaction where trans_no = ' + trans_no
    cursor.execute(query)
    row = list(cursor.fetchone())[0]
    if row:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'This booking ID has already been paid for.',
            'trans_no': trans_no
        })
        return render(request, 'admin_rent.html', context)
    time_rent = "'" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
    query = 'update rental_transaction set time_rent = ' + time_rent + ' where trans_no = ' + trans_no
    cursor.execute(query)

    transaction.commit_unless_managed()

    context = RequestContext(request, {
        'success': True
    })
    return render(request, 'admin_rent.html', context)


def get_trans_details(request, trans_no):
    if not trans_no.isdigit():
        return HttpResponse(json.dumps({
            'error': True,
            'error_msg': 'Booking ID should contain only digits.',
            'trans_no': trans_no
        }))
    cursor = connection.cursor()
    query = 'select customer.u_id,fname,lname,address,license_reg_no,car_type_no,driver_no,advance,no_of_days' \
            ' from rental_transaction,customer where rental_transaction.u_id = customer.u_id and status = 1 and ' \
            'trans_no = ' + trans_no
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        return HttpResponse(json.dumps({
            'error': True,
            'error_msg': 'This booking ID does not exist.',
            'trans_no': trans_no
        }))

    row = list(row)

    data = {
        'uid': row[0],
        'name': row[1] + ' ' + row[2],
        'address': row[3],
        'license_reg_no': row[4],
        'car_type_no': row[5],
        'advance': row[7],
        'no_of_days': row[8]
    }

    if row[6]:
        data['driver_no'] = row[6]

    return HttpResponse(json.dumps(data))


def return_car(request):
    if not request.POST:
        return render(request, 'admin_return.html')
    trans_no = request.POST.get('trans_no')
    no_of_days = int(request.POST.get('no_of_days'))
    cursor = connection.cursor()
    query = 'select time_rent, time_return, car_type_no, license_reg_no, driver_no, advance from ' \
            'rental_transaction where trans_no = ' + trans_no
    cursor.execute(query)
    row = cursor.fetchone()
    row = list(row)
    if row[1]:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'The car rented with this booking ID has already been returned.',
            'trans_no': trans_no
        })
        return render(request, 'admin_return.html', context)
    time_rent = row[0]
    car_type_no = str(row[2])
    license_reg_no = row[3]
    driver_no = row[4]
    advance = row[5]
    distance = 0

    if driver_no:
        driver_no = str(driver_no)
        distance = request.POST.get('dist')
        if not distance:
            context = RequestContext(request, {
                'error': True,
                'error_msg': 'Please enter the distance.',
                'trans_no': trans_no
            })
            return render(request, 'admin_return.html', context)
        distance = int(distance)

    time_return = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "update rental_transaction set time_return = '" + time_return + "' where trans_no = " + trans_no
    cursor.execute(query)

    time_rent = time_rent.strftime("%Y-%m-%d %H:%M:%S")
    diff = datetime.strptime(time_return, "%Y-%m-%d %H:%M:%S") - datetime.strptime(time_rent, "%Y-%m-%d %H:%M:%S")
    days = diff.days
    hours = diff.seconds/(60*60)
    if hours > 0:
        days += 1

    query = 'select min_price, deposit, ac_add, driver_per_km from car_type where car_type_no = ' + car_type_no
    cursor.execute(query)
    row = cursor.fetchone()
    row = list(row)
    min_price = row[0]
    deposit = row[1]
    ac_add = row[2]
    driver_per_km = row[3]
    extra_amount = 0
    driver_charges = 0
    days_extra = days - no_of_days

    if days_extra > 0:
        extra_amount += days_extra * min_price
        query = "select ac from car where license_Reg_no = '" + license_reg_no + "'"
        cursor.execute(query)
        row = list(cursor.fetchone())
        if row[0]:
            extra_amount += days_extra * ac_add

    if driver_no:
        query = 'update rental_transaction set distance = ' + str(distance) + ' where trans_no = ' + trans_no
        cursor.execute(query)
        driver_charges += driver_per_km * distance
        query = 'select total_days from driver where driver_no = ' + driver_no
        cursor.execute(query)
        total_days = list(cursor.fetchone())[0]
        if total_days:
            total_days = int(total_days)
            total_days += days
        else:
            total_days = days
        query = 'update driver set total_days = ' + str(total_days) + ' where driver_no = ' + driver_no
        cursor.execute(query)
        query = 'update driver set salary = ' + str(total_days*SALARY_PER_DAY) + ' where driver_no = ' + driver_no
        cursor.execute(query)
        query = 'update driver set avail = 1 where driver_no = ' + driver_no
        cursor.execute(query)
        query = "update car set driver_no = null where license_reg_no = '" + license_reg_no + "'"
        cursor.execute(query)

    rental_amount = advance + extra_amount + driver_charges - deposit
    return_amt = advance - rental_amount

    query = 'update rental_transaction set rental_amt = ' + str(rental_amount) + ' where trans_no = ' + trans_no
    cursor.execute(query)
    query = 'update rental_transaction set status = 2 where trans_no = ' + trans_no
    cursor.execute(query)
    query = "update car set cust_uid = null where license_reg_no = '" + license_reg_no + "'"
    cursor.execute(query)

    query = "select * from rental_transaction where trans_no = " + trans_no
    cursor.execute(query)
    row = cursor.fetchone()
    row = list(row)

    trans_log = str(row[0])+"|"+str(row[1])+"|"+str(row[2])+"|"+str(row[3])+"|"+str(row[4])+"|"+str(row[5])+"|"+str(row[6])+"|"+str(row[7])+"|"+str(row[8])+"|"+str(row[9])+"|"+str(row[10])+"|"+str(row[11])+"\n"
    f = open('transactions.txt', 'a')
    f.write(trans_log)
    f.close()

    transaction.commit_unless_managed()

    day = 'days' if days_extra > 1 else 'day'
    ret = True if return_amt > 0 else False
    return_amt = abs(return_amt)
    context = RequestContext(request, {
        'success': True,
        'advance': advance,
        'driver_charges': driver_charges,
        'extra_amount': extra_amount,
        'no_of_days': no_of_days,
        'days_extra': days_extra,
        'day': day,
        'deposit': deposit,
        'total_amount': rental_amount,
        'return_amt': return_amt,
        'ret': ret,
        'driver_per_km': driver_per_km
    })
    return render(request, 'admin_return.html', context)


def add_car(request):
    if not request.POST:
        return render(request, 'add_car.html')
    license_reg_no = request.POST.get('license_reg_no')
    model_no = request.POST.get('model_no')
    color = request.POST.get('color')
    ac = request.POST.get('ac')
    if not license_reg_no or not model_no or not color or not ac:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Please enter all details.',
            'license_reg_no': license_reg_no,
            'model_no': model_no,
            'color': color,
            'ac': ac
        })
        return render(request, 'add_car.html', context)
    try:
        error = False
        if len(license_reg_no) > 10:
            error = True
            error_msg = 'License number cannot be more than 10 characters.'
        elif not model_no.isdigit():
            error = True
            error_msg = 'Model number should be a number.'
        elif len(color) > 10:
            error = True
            error_msg = 'Color cannot be more than 10 characters.'
        if error:
            context = RequestContext(request, {
                'error': True,
                'error_msg': error_msg,
                'license_reg_no': license_reg_no,
                'model_no': model_no,
                'color': color,
                'ac': ac
            })
            return render(request, 'add_car.html', context)
        cursor = connection.cursor()
        query = "select * from car where license_reg_no = '" + license_reg_no + "'"
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            context = RequestContext(request, {
                'error': True,
                'error_msg': 'Car with this license number already exists.',
                'license_reg_no': license_reg_no,
                'model_no': model_no,
                'color': color,
                'ac': ac
            })
            return render(request, 'add_car.html', context)
        query = "insert into car(license_reg_no,model_no,color,ac) values('" + license_reg_no + "'," + model_no + "," \
                                                                                    "'" + color + "'," + ac + ")"

        cursor.execute(query)
        transaction.commit_unless_managed()
        context = RequestContext(request, {
            'success': True
        })
        return render(request, 'add_car.html', context)

    except IntegrityError:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Model number entered does not exist.',
            'license_reg_no': license_reg_no,
            'model_no': model_no,
            'color': color,
            'ac': ac
        })
        return render(request, 'add_car.html', context)
    except:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Internal Server Error. Please try later.',
            'license_reg_no': license_reg_no,
            'model_no': model_no,
            'color': color,
            'ac': ac
        })
        return render(request, 'add_car.html', context)


def remove_car(request):
    if not request.POST:
        return render(request, 'remove_car.html')
    license_reg_no = request.POST.get('license_reg_no')
    error = False
    error_msg = ''
    if not license_reg_no:
        error = True
        error_msg = 'Please enter License Registration Number.'
    elif len(license_reg_no) > 10:
        error = True
        error_msg = 'License Registration Number should not be more than 10 characters.'
    if error:
        context = RequestContext(request, {
            'error': True,
            'error_msg': error_msg,
            'license_reg_no': license_reg_no
        })
        return render(request, 'remove_car.html', context)
    cursor = connection.cursor()
    query = "select cust_uid from car where license_reg_no = '" + license_reg_no + "'"
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        error = True
        error_msg = "No such License Registration Number."
    elif list(row)[0]:
        error = True
        error_msg = "This car has been rented by a customer. Please try after it has been returned."
    if error:
        context = RequestContext(request, {
            'error': error,
            'error_msg': error_msg,
            'license_reg_no': license_reg_no
        })
        return render(request, 'remove_car.html', context)
    query = "select license_reg_no from rental_transaction where license_reg_no = '" + license_reg_no + "'"
    cursor.execute(query)
    row = cursor.fetchall()
    if row:
        query = "delete from rental_transaction where license_reg_no = '" + license_reg_no + "'"
        cursor.execute(query)
    query = "delete from car where license_reg_no = '" + license_reg_no + "'"
    cursor.execute(query)

    transaction.commit_unless_managed()
    context = RequestContext(request, {
        'success': True,
        'license_reg_no': license_reg_no,
    })
    return render(request, 'remove_car.html', context)


def add_driver(request):
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
        return render(request, 'add_driver.html', context)
    driver_no = request.POST.get('driver_no')
    uid = request.POST.get('uid')
    name = request.POST.get('name')
    phone_no = request.POST.get('phone_no')
    place = request.POST.get('place')
    if not driver_no or not uid or not name or not phone_no or not place:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Please enter all details.',
            'driver_no': driver_no,
            'uid': uid,
            'name': name,
            'phone_no': phone_no,
            'place': place,
            'place_list': place_list
        })
        return render(request, 'add_driver.html', context)
    try:
        error = False
        error_msg = ''
        if not driver_no.isdigit():
            error = True
            error_msg = 'Driver number should contain only digits.'
        elif not uid.isdigit():
            error = True
            error_msg = 'UID should contain only digits.'
        elif len(driver_no) > 20:
            error = True
            error_msg = 'Driver number cannot contain more than 20 digits.'
        elif len(uid) != 12:
            error = True
            error_msg = 'UID cannot contain more than 12 digits.'
        elif len(name) > 30:
            error = True
            error_msg = 'Name should have max. 30 characters.'
        elif not re.match("^[a-zA-Z ]*$", name):
            error = True
            error_msg = 'Name should have only alphabets and spaces.'
        elif len(phone_no) != 10 or not phone_no.isdigit():
            error = True
            error_msg = 'Invalid phone number.'
        if error:
            context = RequestContext(request, {
                'error': True,
                'error_msg': error_msg,
                'driver_no': driver_no,
                'uid': uid,
                'name': name,
                'phone_no': phone_no,
                'place': place,
                'place_list': place_list
            })
            return render(request, 'add_driver.html', context)
        query = "select * from driver where driver_no = " + driver_no
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            context = RequestContext(request, {
                'error': True,
                'error_msg': 'Driver with this driver number already exists.',
                'driver_no': driver_no,
                'uid': uid,
                'name': name,
                'phone_no': phone_no,
                'place': place,
                'place_list': place_list
            })
            return render(request, 'add_driver.html', context)
        query = "select place_no from place where place_name = '" + place + "'"
        cursor.execute(query)
        place_no = str(list(cursor.fetchone())[0])
        print phone_no
        query = "insert into driver(driver_no,u_id,name,ph_no,place_no) values(" + driver_no + "," + uid + "," \
                                                                                    "'" + name + "'," + phone_no + "," + place_no + ")"

        print query
        cursor.execute(query)
        transaction.commit_unless_managed()
        context = RequestContext(request, {
            'success': True
        })
        return render(request, 'add_driver.html', context)

    except IntegrityError:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Model number entered does not exist.',
            'driver_no': driver_no,
            'uid': uid,
            'name': name,
            'phone_no': phone_no,
            'place': place,
            'place_list': place_list
        })
        return render(request, 'add_driver.html', context)
    except:
        context = RequestContext(request, {
            'error': True,
            'error_msg': 'Internal Server Error. Please try later.',
            'driver_no': driver_no,
            'uid': uid,
            'name': name,
            'phone_no': phone_no,
            'place': place,
            'place_list': place_list
        })
        return render(request, 'add_driver.html', context)


def remove_driver(request):
    if not request.POST:
        return render(request, 'remove_driver.html')
    driver_no = request.POST.get('driver_no')
    error = False
    error_msg = ''
    if not driver_no:
        error = True
        error_msg = 'Please enter Driver Number.'
    elif len(driver_no) > 20:
        error = True
        error_msg = 'Driver Number should not be more than 20 digits.'
    elif not driver_no.isdigit():
        error = True
        error_msg = 'Driver Number should contain only digits.'
    if error:
        context = RequestContext(request, {
            'error': True,
            'error_msg': error_msg,
            'driver_no': driver_no
        })
        return render(request, 'remove_driver.html', context)
    cursor = connection.cursor()
    query = "select avail from driver where driver_no = " + driver_no
    cursor.execute(query)
    row = cursor.fetchone()
    if not row:
        error = True
        error_msg = "No such Driver."
    elif not list(row)[0]:
        error = True
        error_msg = "This driver has been hired by a customer. Please try again later."
    if error:
        context = RequestContext(request, {
            'error': error,
            'error_msg': error_msg,
            'driver_no': driver_no
        })
        return render(request, 'remove_driver.html', context)
    query = "select driver_no from rental_transaction where driver_no = " + driver_no
    cursor.execute(query)
    row = cursor.fetchall()
    if row:
        query = "delete from rental_transaction where driver_no = '" + driver_no + "'"
        cursor.execute(query)
    query = "delete from driver where driver_no = " + driver_no
    cursor.execute(query)

    transaction.commit_unless_managed()
    context = RequestContext(request, {
        'success': True,
        'driver_no': driver_no,
    })
    return render(request, 'remove_driver.html', context)