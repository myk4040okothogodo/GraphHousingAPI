# Generated by Django 3.2.13 on 2022-05-17 20:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('BuildingsAPI_Payments', '0001_initial'),
        ('BuildingsAPI_Users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('BuildingsAPI_Houses', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentimage',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paymentreceipt_images', to='BuildingsAPI_Users.imageupload'),
        ),
        migrations.AddField(
            model_name='paymentimage',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_images', to='BuildingsAPI_Payments.payment'),
        ),
        migrations.AddField(
            model_name='payment',
            name='categories',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_categories', to='BuildingsAPI_Payments.category'),
        ),
        migrations.AddField(
            model_name='payment',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BuildingsAPI_Houses.house'),
        ),
        migrations.AddField(
            model_name='payment',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments_tenantid', to=settings.AUTH_USER_MODEL),
        ),
    ]
