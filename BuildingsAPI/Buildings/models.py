from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from BuildingsAPI.Users.models import ImageUpload



class Category(models.Model):
    
    SINGLE_ROOMS = 1
    BED_SITTERS  = 2
    ONE_BEDROOMS = 3
    TWO_BEDROOMS = 4
    THREE_BEDROOMS = 5
    FOUR_BEDROOMS = 6
    MANSION = 7
    BUILDING_CATEGORY = (
        (SINGLE_ROOMS, _('single_rooms')),
        (BED_SITTERS,  _('bed_sitters')),
        (ONE_BEDROOMS, _('one_bedrooms')),
        (TWO_BEDROOMS, _('two_bedrooms')),
        (THREE_BEDROOMS, _('three_bedrooms')),
        (FOUR_BEDROOMS, _('four_bedrooms')),
        (MANSION, _('mansion')),
            )
    name = models.CharField(max_length=100, unique=True)
    building_category = models.PositiveSmallIntegerField(choices=BUILDING_CATEGORY, primary_key=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    """A building or apartment of multiple rooms housing tenants."""
    building_category = models.ForeignKey(Category, related_name="categoryOf_building", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False, default='')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="building_owner", on_delete=models.CASCADE)
    careTaker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="building_caretaker", on_delete=models.CASCADE)
    dateCommissioned = models.DateField()
    starsRating = models.IntegerField()
    account_no  = models.IntegerField(blank=False, null=False)


    def __str__(self):
        return f"{self.name}"

    def building_age():
        pass


class BuildingImage(models.Model):
    building = models.ForeignKey(Building, related_name="building_images", on_delete=models.CASCADE)
    image    = models.ForeignKey(ImageUpload, related_name="image_building", on_delete=models.CASCADE)
    is_cover  = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"{self.building.name} - {self.image}"


class BuildingComment(models.Model):
    building = models.ForeignKey(Building, related_name="building_comments", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_comments", on_delete=models.CASCADE)
    comment = models.TextField()
    rate = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
