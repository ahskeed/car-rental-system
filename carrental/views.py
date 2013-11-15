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
    cursor = connection.cursor()
    if model_name == 'merc_eclass':
        model_name = 'MERCEDES E CLASS'
    elif model_name == 'merc_sclass':
        model_name = 'MERCEDES S CLASS'
    elif model_name == 'bmw_5':
        model_name = 'BMW 5 SERIES'
    elif model_name == 'bmw_7':
        model_name = 'BMW 7 SERIES'

    elif model_name == 'honda_accord':
        model_name = 'HONDA ACCORD'
    elif model_name == 'toyota_camry':
        model_name = 'TOYOTA CAMRY'
    elif model_name == 'toyota_corolla':
        model_name = 'TOYOTA COROLLA'

    elif model_name == 'honda_city':
        model_name = 'HONDA CITY'
    elif model_name == 'hyundai_verna':
        model_name = 'HYUNDAI VERNA'
    elif model_name == 'mit_lancer':
        model_name = 'MITSUBISHI LANCER'

    elif model_name == 'ambassador':
        model_name = 'AMBASSADOR'
    elif model_name == 'tata_indigo':
        model_name = 'TATA INDIGO'
    elif model_name == 'hyundai_accent':
        model_name = 'HYUNDAI ACCENT'

    elif model_name == 'toyota_cruiser':
        model_name = 'TOYOTA LAND CRUISER'
    elif model_name == 'tata_safari':
        model_name = 'TATA MOTORS SAFARI'
    elif model_name == 'toyota_qualis':
        model_name = 'TOYOTA QUALIS'
    elif model_name == 'innova':
        model_name = 'INNOVA'

    query = "select * from model where name = '" + model_name + "'"
    print query
    row = Model.objects.raw(query)
    model_list = list(row)

    context = RequestContext(request, {
        'model_name': model_list[0],
        'price': model_list[0].car_type_no.min_price,
        'ac_add': model_list[0].car_type_no.ac_add,
        'deposit': model_list[0].car_type_no.deposit
    })
    cursor.close()
    return render(request, 'model_name_details.html', context)






