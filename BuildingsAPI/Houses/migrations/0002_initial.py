# Generated by Django 3.2.13 on 2022-05-17 20:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('BuildingsAPI_Houses', '0001_initial'),
        ('BuildingsAPI_Buildings', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('BuildingsAPI_Users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='houseimage',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_house', to='BuildingsAPI_Users.imageupload'),
        ),
        migrations.AddField(
            model_name='housecomment',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='house_comments', to='BuildingsAPI_Houses.house'),
        ),
        migrations.AddField(
            model_name='housecomment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userwho_comments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='house',
            name='building',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='BuildingsAPI_Buildings.building'),
        ),
        migrations.AddField(
            model_name='house',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='house_category', to='BuildingsAPI_Houses.category'),
        ),
        migrations.AddField(
            model_name='house',
            name='tenant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='house_tenants', to=settings.AUTH_USER_MODEL),
        ),
    ]