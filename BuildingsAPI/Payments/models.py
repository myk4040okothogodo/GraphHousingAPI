from django.db import models
from django.conf import settings
from BuildingsAPI.Houses.models import House
from BuildingsAPI.Users.models import ImageUpload
import moneyed
from djmoney.models.fields import MoneyField
from datetime import datetime




class Category(models.Model):
    RENT = 1
    REPAIRS = 2
    WATER_BILL = 3
    GARBAGE_COLLECTION = 4
    PAYMENT_TYPE = (
        (RENT, _('rent')),
        (REPAIRS, _('repairs')),
        (WATER_BILL, ('water_bill')),
        (GARBAGE_COLLECTION, ('garbage_collection')),
            )
    payment_category = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE, primary_keys=True)

    def __str__(self):
        return self.payment_category


class Payment(models.Model):
    """This class represents rent/utility payments made by the tenants. """
    payment_type =  models.ForeignKey(Category, related_name="payment_categories", on_delete=models.CASCADE)
    room = models.ForeignKey(House,blank=False, null=False, on_delete=models.CASCADE)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL,blank=False,related_name="payments_tenantid", null=False, on_delete=models.CASCADE)
    amount_paid = MoneyField(max_digits=10, decimal_places=2, default_currency='KES')
    receipt_no = models.IntegerField(blank=False,null=False)
    date = models.DateTimeField(default=datetime.now, blank=False)

    def __str__(self):
        return f"{self.receipt_no}"


class PaymentImage(models.Model):
    payment = models.ForeignKey(Payment, related_name="payment_images", on_delete=models.CASCADE)
    image = models.ForeignKey(ImageUpload, related_name="paymentreceipt_images", on_delete=models.CASCADE)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment.room.house_number} - {self.payment.tenant.name} - {self.image}"
