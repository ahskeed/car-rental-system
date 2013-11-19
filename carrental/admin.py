from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection, transaction
from django.template import RequestContext
import json

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
    return  HttpResponse(json.dumps(data))


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
    driver_no = str(row[4])
    advance = row[5]
    distance = 0

    if driver_no:
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
        query = 'select tot_hours from driver where driver_no = ' + driver_no
        cursor.execute(query)
        tot_hours = list(cursor.fetchone())[0]
        if tot_hours:
            tot_hours = int(tot_hours)
            tot_hours += days
        else:
            tot_hours = days
        query = 'update driver set tot_hours = ' + str(tot_hours) + ' where driver_no = ' + driver_no
        cursor.execute(query)
        query = 'update driver set salary = ' + str(tot_hours*SALARY_PER_DAY) + ' where driver_no = ' + driver_no
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