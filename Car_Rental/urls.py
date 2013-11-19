from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'carrental.views.home', name='home'),
    url(r'^rent$', 'carrental.views.view_car_types'),
    url(r'^rent/customer_details/(?P<model_name>\w+)$', 'carrental.views.customer_details'),
    url(r'^rent/model/(?P<model_name>\w+)$', 'carrental.views.model_name_details'),
    url(r'^rent/(?P<car_type>\w+)$', 'carrental.views.view_car_type_details'),

    url(r'^cancel', 'carrental.views.cancel_transaction'),
    url(r'^get_details/(?P<trans_no>\w+)/(?P<uid>\w+)$', 'carrental.views.get_details'),

    url(r'^admin$', 'carrental.admin.home'),
    url(r'^admin/rent$', 'carrental.admin.rent'),
    url(r'^admin/return$', 'carrental.admin.return_car'),
    url(r'^admin/get_trans_details/(?P<trans_no>\w+)$', 'carrental.admin.get_trans_details'),
    url(r'^admin/pay_driver', 'carrental.admin.pay_driver'),
    url(r'^admin/get_driver_details/(?P<driver_no>\w+)$', 'carrental.admin.get_driver_details'),
    url(r'^admin/add_car', 'carrental.admin.add_car'),
    url(r'^admin/remove_car', 'carrental.admin.remove_car'),
    url(r'^admin/add_driver', 'carrental.admin.add_driver'),
    url(r'^admin/remove_driver', 'carrental.admin.remove_driver'),


    # url(r'^Car_Rental/', include('Car_Rental.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)