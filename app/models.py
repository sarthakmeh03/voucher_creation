# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.core.mail import EmailMessage
import pdfkit
import os
from django.template.loader import get_template
from datetime import date
import time
from threading import Thread

voucher_type_choices = (
    ('himachal', 'Himachal'),
    ('goa', 'Goa'),
    ('andaman', 'Andaman'),
    ('normal', 'Normal')
)


class QuoteVoucher(models.Model):
    type = models.CharField(choices=voucher_type_choices, max_length=100)
    confirmed = models.BooleanField()
    name_of_guest = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email_id = models.CharField(max_length=200)
    no_of_pax = models.CharField(max_length=200)
    package_type = models.CharField(max_length=200)
    arrival = models.DateField()
    pickup_place = models.CharField(max_length=200)
    no_of_rooms = models.CharField(max_length=200)
    price = models.CharField(max_length=100)
    package_inclusion = models.TextField()
    package_exclusion = models.TextField()
    reservation_policy = models.TextField()
    cancellation_policy = models.TextField()
    terms_conditions = models.TextField()

    def save(self, *args, **kwargs):
        Worker(self).start()
        return super(QuoteVoucher, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name_of_guest


class Itenary(models.Model):
    voucher = models.ForeignKey(QuoteVoucher)
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __unicode__(self):
        return self.title


class Hotel(models.Model):
    voucher = models.ForeignKey(QuoteVoucher)
    name = models.CharField(max_length=255)
    check_in = models.DateField()
    check_out = models.DateField()
    address = models.TextField(blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    contact_person_position = models.CharField(max_length=200, blank=True)
    place = models.CharField(max_length=100)
    meal_plan = models.CharField(max_length=100)
    room_type = models.CharField(max_length=200)
    occupancy_type = models.CharField(max_length=200)
    no_of_rooms = models.IntegerField()
    no_of_nights = models.IntegerField()
    confirmation_number = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name


class Vehicle(models.Model):
    voucher = models.ForeignKey(QuoteVoucher)
    category = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    no_of_vehicle = models.IntegerField()
    no_of_days = models.IntegerField()
    contact_person = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12)
    service_provider = models.CharField(max_length=100)
    confirmation_number = models.CharField(max_length=200, blank=True)

    def __unicode__(self):
        return self.name


class SpecialService(models.Model):
    voucher = models.ForeignKey(QuoteVoucher)
    date = models.DateField()
    service = models.CharField(max_length=200)
    description = models.TextField()


class Worker(Thread):
    def __init__(self, voucher):
        super(Worker, self).__init__()
        self.voucher = voucher

    def run(self):
        time.sleep(20)
        print "Sending Mail....."
        self = self.voucher
        output_path = os.getcwd() + '/templates/output/test.pdf'
        if not self.confirmed:
            # NORMAL VOUCHER
            if self.type == 'normal':
                data = {'current_date': date.today(),
                        'image_path': os.getcwd() + '/templates/images/logo.png',
                        'no_of_pax': self.no_of_pax,
                        'arrival': self.arrival,
                        'departure': self.pickup_place,
                        'rooms': self.no_of_rooms,
                        'duration': self.package_type,
                        'itinerary': self.itenary_set.all().values(),
                        'hotels': self.hotel_set.all().values(),
                        'vehicle': self.vehicle_set.all().values(),
                        'amount': self.price,
                        'inclusion': self.package_inclusion.split("\n"),
                        'exclusion': self.package_exclusion.split("\n"),
                        'reservation_policy': self.reservation_policy.split("\n"),
                        'cancellation_policy': self.cancellation_policy.split("\n"),
                        'terms': self.terms_conditions.split("\n"),
                        'special_service': self.specialservice_set.all().values()}
                output_path = os.getcwd() + '/templates/output/' + self.name_of_guest + ".pdf"
                template = get_template('quoteVoucher.html')
                html = template.render(data)
                pdfkit.from_string(html, output_path)
                msg = EmailMessage('Quote Voucher', 'Please find the quotation attached', 'sarthakmeh03@gmail.com',
                                   [self.email_id])
                msg.content_subtype = "html"
                msg.attach_file(output_path)
                msg.send()
                # ANDAMAN VOUCHER
            elif self.type == 'andaman':
                data = {'current_date': date.today(),
                        'image_path': os.getcwd() + '/templates/images/logo.png',
                        'confirmation_no': self.hotel_set.all().values()[0]['confirmation_number'],
                        'tour_manager': self.hotel_set.all().values()[0]['contact_person'] + " - " +
                                        str(self.hotel_set.all().values()[0]['phone_number']),
                        'city': self.package_type,
                        'hotels': self.hotel_set.all().values(),
                        'name_of_guest': self.name_of_guest,
                        'arrival': self.arrival,
                        'pickup_place': self.pickup_place,
                        'rooms': self.no_of_rooms,
                        'no_of_pax': self.no_of_pax,
                        'meal_plan': self.hotel_set.all().values()[0]['meal_plan'],
                        'vehicle_name': self.vehicle_set.all().values()[0]['name'],
                        'itinerary': self.itenary_set.all().values()}
                template = get_template('andamanVoucher.html')
                html = template.render(data)
                pdfkit.from_string(html, output_path)
                msg = EmailMessage('Andaman Voucher', 'Please find the quotation attached', 'sarthakmeh03@gmail.com',
                                   [self.email_id])
                msg.content_subtype = "html"
                msg.attach_file(output_path)
                msg.send()
                # GOA VOUCHER
            elif self.type == 'goa':
                hotel = self.hotel_set.all().values()[0]
                data = {'current_date': date.today(),
                        'image_path': os.getcwd() + '/templates/images/logo.png',
                        'confirmation_no': self.hotel_set.all().values()[0]['confirmation_number'],
                        'hotel': hotel['name'] + "<br />\n" + hotel['address'],
                        'name_of_guest': self.name_of_guest,
                        'check_in': hotel['check_in'],
                        'check_out': hotel['check_out'],
                        'no_of_pax': self.no_of_pax,
                        'no_of_nights': hotel['no_of_nights'],
                        'rooms': self.no_of_rooms,
                        'room_type': hotel['room_type'],
                        'meal_plan': hotel['meal_plan'],
                        'inclusion': self.package_inclusion.split("\n"),
                        'cancellation_policy': self.cancellation_policy.split("\n")}
                template = get_template('goaVoucher.html')
                html = template.render(data)
                pdfkit.from_string(html, output_path)
                msg = EmailMessage('Goa Voucher', 'Please find the quotation attached', 'sarthakmeh03@gmail.com',
                                   [self.email_id])
                msg.content_subtype = "html"
                msg.attach_file(output_path)
                msg.send()
            # HIMACHAL VOUCHER
            elif self.type == 'himachal':
                data = {'current_date': date.today(),
                        'image_path': os.getcwd() + '/templates/images/logo.png',
                        'confirmation_no': self.hotel_set.all().values()[0]['confirmation_number'],
                        'tour_manager': self.hotel_set.all().values()[0]['contact_person'] + " - " +
                                        str(self.hotel_set.all().values()[0]['phone_number']),
                        'city': self.package_type,
                        'hotels': self.hotel_set.all().values(),
                        'name_of_guest': self.name_of_guest,
                        'arrival': self.arrival,
                        'pickup_place': self.pickup_place,
                        'rooms': self.no_of_rooms,
                        'no_of_pax': self.no_of_pax,
                        'vehicle_name': self.vehicle_set.all().values()[0]['name'],
                        'itinerary': self.itenary_set.all().values()}
                template = get_template('himachalVoucher.html')
                html = template.render(data)
                pdfkit.from_string(html, output_path)
                msg = EmailMessage('Himachal Voucher', 'Please find the quotation attached', 'sarthakmeh03@gmail.com',
                                   [self.email_id])
                msg.content_subtype = "html"
                msg.attach_file(output_path)
                msg.send()
        # HOTEL AND DRIVER VOUCHER
        else:
            msg = EmailMessage('Hotel and Driver Voucher', 'Please find the voucher attached', 'sarthakmeh03@gmail.com',
                               [self.email_id])
            for i in self.hotel_set.all().values():
                data = {'current_date': date.today(),
                        'image_path': os.getcwd() + '/templates/images/logo.png',
                        'hotel_name': i['name'],
                        'address': i['address'],
                        'guest_name': self.name_of_guest,
                        'check_in': i['check_in'],
                        'check_out': i['check_out'],
                        'no_of_pax': self.no_of_pax,
                        'meal_plan': i['meal_plan'],
                        'room_type': i['room_type'],
                        'no_of_nights': i['no_of_nights'],
                        'occupancy_type': i['occupancy_type'],
                        'no_of_rooms': i['no_of_rooms'],
                        'contact_name': i['contact_person'],
                        'mobile_no': i['phone_number'],
                        'contact_position': i['contact_person_position'],
                        'place': i['place'],
                        'confirmation_no': i['confirmation_number']
                        }
                template = get_template('hotelVoucher.html')
                html = template.render(data)
                pdfkit.from_string(html, output_path)
                msg.content_subtype = "html"
                msg.attach_file(output_path)
            driver_data = {'current_date': date.today(),
                           'confirmation_no': self.vehicle_set.all().values()[0]['confirmation_number'],
                           'guest_name': self.name_of_guest,
                           'image_path': os.getcwd() + '/templates/images/logo.png',
                           'arrival': self.arrival,
                           'departure': self.pickup_place,
                           'duration': self.package_type,
                           'itinerary': self.itenary_set.all().values,
                           'hotels': self.hotel_set.all().values,
                           'vehicle': self.vehicle_set.all().values,
                           'special_service': self.specialservice_set.all().values}
            template = get_template('driverVoucher.html')
            html = template.render(driver_data)
            pdfkit.from_string(html, output_path)
            msg.content_subtype = "html"
            msg.attach_file(output_path)
            msg.send()
