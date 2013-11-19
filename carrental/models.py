from django.db import models


class PhoneNum(models.Model):
    u_id = models.BigIntegerField()
    ph_no = models.BigIntegerField()

    class Meta:
        managed = True
        db_table = 'phone_num'


class Car(models.Model):
    license_reg_no = models.CharField(primary_key=True, max_length=10)
    model_no = models.ForeignKey('Model', db_column='model_no')
    driver_no = models.ForeignKey('Driver', db_column='driver_no', blank=True, null=True)
    cust_uid = models.BigIntegerField(blank=True, null=True)
    color = models.CharField(max_length=10, blank=True)
    ac = models.IntegerField(blank=True, null=True)
    at_service = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'car'


class CarType(models.Model):
    car_type_no = models.BigIntegerField(primary_key=True)
    cartype = models.CharField(max_length=20)
    min_price = models.DecimalField(max_digits=6, decimal_places=2)
    deposit = models.DecimalField(max_digits=7, decimal_places=2)
    ac_add = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    driver_per_km = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'car_type'


class Customer(models.Model):
    u_id = models.BigIntegerField(primary_key=True)
    fname = models.CharField(max_length=20)
    lname = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=100)
    lic_no = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'customer'


class Driver(models.Model):
    driver_no = models.BigIntegerField(primary_key=True)
    u_id = models.BigIntegerField()
    name = models.CharField(max_length=30)
    ph_no = models.BigIntegerField()
    place_no = models.ForeignKey('Place', db_column='place_no')
    total_days = models.BigIntegerField(blank=True, null=True)
    salary = models.BigIntegerField(blank=True, null=True)
    avail = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'driver'


class Model(models.Model):
    model_no = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    seat_capacity = models.BigIntegerField(blank=True, null=True)
    fuel_capacity = models.BigIntegerField(blank=True, null=True)
    eng_capacity = models.BigIntegerField(blank=True, null=True)
    fuel_type = models.CharField(max_length=2)
    height = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    car_type_no = models.ForeignKey(CarType, db_column='car_type_no')

    class Meta:
        managed = True
        db_table = 'model'


class Place(models.Model):
    place_no = models.BigIntegerField(primary_key=True)
    place_name = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'place'


class RentalTransaction(models.Model):
    trans_no = models.AutoField(primary_key=True)
    u_id = models.ForeignKey(Customer, db_column='u_id')
    license_reg_no = models.ForeignKey(Car, db_column='license_reg_no')
    car_type_no = models.ForeignKey(CarType, db_column='car_type_no')
    driver_no = models.ForeignKey(Driver, db_column='driver_no', blank=True, null=True)
    time_rent = models.DateTimeField(blank=True, null=True)
    time_return = models.DateTimeField(blank=True, null=True)
    distance = models.BigIntegerField(default=0, blank=True, null=True)
    advance = models.BigIntegerField(blank=True, null=True)
    rental_amt = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    no_of_days = models.IntegerField()
    status = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'rental_transaction'