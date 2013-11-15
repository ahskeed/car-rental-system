# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
from django.template import RequestContext
from carrental.models import RentalTransaction
import json


def home(request):
    return render(request, 'admin_home.html')


def trans_details(request):
    return render(request, 'admin_rent.html')


def get_trans_details(request, trans_no):
    cursor = connection.cursor()
    query = 'select customer.u_id,fname,lname,address,license_reg_no,car_type_no,driver_no,time_rent,advance,no_of_days' \
            ' from rental_transaction,customer where rental_transaction.u_id = customer.u_id and ' \
            'trans_no = ' + trans_no
    cursor.execute(query)
    row = cursor.fetchone()
    row = list(row)

    return HttpResponse(json.dumps({'uid': row[0],
                                    'name': row[1] + ' ' + row[2],
                                    'address': row[3],
                                    'license_reg_no': row[4],
                                    'car_type_no': row[5],
                                    'driver_no': row[6],
                                    'advance': row[8],
                                    'no_of_days': row[9]
    }), mimetype="application/json")



