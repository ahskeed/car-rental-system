# Create your views here.
from django.shortcuts import render
from django.db import connection
from django.template import RequestContext
from carrental.models import Model


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
        name = 'HYUNDAI VERNA'
    elif model_name == 'mit_lancer':
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
    query = "select model_no from car where model_no = " + str(model_list[0].model_no)
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
        'place_list': place_list,
        'driver': True
    })
    if not request.POST:
        return render(request, 'customer_details.html', context)
    else:
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        address = request.POST.get('address')
        return render(request, 'customer_details.html')






