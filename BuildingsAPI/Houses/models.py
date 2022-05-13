from django.db import models
from django.conf import settings
from ..Buildings.models import Building
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    
    SINGLE_ROOM = 1
    BED_SITTER = 2
    ONE_BEDROOM = 3
    TWO_BEDROOM = 4
    THREE_BEDROOM = 5
    FOUR_BEDROOM = 6
    MANSION = 7
    HOUSE_CATEGORY = (
        (SINGLE_ROOM, _('single_room')),
        (BED_SITTER,  _('bed_sitter')),
        (ONE_BEDROOM, _('one_bedroom')),
        (TWO_BEDROOM, _('two_bedroom')),
        (THREE_BEDROOM, _('three_bedroom')),
        (FOUR_BEDROOM, _('four_bedroom')),
        (MANSION, _('mansion')),
            )
    house_category = models.PositiveSmallIntegerField(choices=HOUSE_CATEGORY, primary_key=True)

    def __str__(self):
        return self.house_category


class House(models.Model):
    """A single unit in a building that houses the tenant."""
    building = models.OneToOneField(Building, blank=False, null=False, on_delete=Models.CASCADE)
    house_category = models.ForeignKey(Category, related_name = "house_category", on_delete=models.CASCADE)
    house_number = models.IntegerField(blank=False, null=False)
    floor_no = models.IntegerField(blank=False, null=False)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="house_tenants", null=True, on_delete=models.CASCADE)
    occupied = models.BooleanField(default=False)


class HouseImage(models.Model):
    house = models.ForeignKey(House, related_name="house_images", on_delete=models.CASCADE)
    image    = models.ForeignKey(ImageUpload, related_name="image_house", on_delete=models.CASCADE)
    is_cover  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.house.building.name} - {self.house.house_number} - {self.image}"


class HouseComment(models.Model):
    house = models.ForeignKey(House, related_name="house_comments", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_comments", on_delete=models.CASCADE)
    comment = models.TextField()
    rate = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
