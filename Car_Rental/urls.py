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
    url(r'^admin/transaction_details$', 'carrental.admin.trans_details'),
    url(r'^admin/get_trans_details/(?P<trans_no>\w+)$', 'carrental.admin.get_trans_details'),

    # url(r'^Car_Rental/', include('Car_Rental.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)