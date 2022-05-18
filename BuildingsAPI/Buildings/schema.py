import graphene
from graphene_django import DjangoObjectType
from GraphQLBuildingsAPI.permissions import paginate, is_authenticated, get_query
from django.db.models import Q

from .models import (Category, Building, BuildingImage, BuildingComment)


class BuildingCategoryType(DjangoObjectType):
    class Meta:
        model = Category
    

class BuildingType(DjangoObjectType):
    class Meta:
        model = Building

class BuildingImageType(DjangoObjectType):
    class Meta:
        model = BuildingImage

class BuildingCommentType(DjangoObjectType):
    class Meta:
        model = BuildingComment


class Query(graphene.ObjectType):
    buildingcategories = graphene.List(BuildingCategoryType, name=graphene.String())
    buildings = graphene.Field(paginate(BuildingType), search=graphene.String(),
        min_rent=graphene.Float(), max_rent=graphene.Float(), category=graphene.String(),
        sort_by=graphene.String(), is_asc=graphene.Boolean(), mine=graphene.Boolean())
    building = graphene.Field(BuildingType, id=graphene.ID(required=True))


    def resolve_buildingcategories(self, info, name=False):
        query = BuildingCategory.objects.prefetch_related("building_categories")

        if name:
            query = query.filter(Q(name_icontains=name) | Q(name_iexact=name)).distinct()
        return query

    @is_authenticated
    def resolve_buildings(self, info, **kwargs):
        mine = kwargs.get("mine", False)
        if mine and not info.context.user:
            raise Exception("User auth required")

        query = Building.objects.select_related("category").prefetch_related(
            "building_images", "building_comments", "building_requests"
                )
        if mine:
            query = query.filter(building__user_id = info.context.user.id)

        if kwargs.get("search", None):
            qs = kwargs["search"]
            search_fields = (
                "name", "owner", "category__name"
                    )

            search_data = get_query(qs, search_fields)
            query = query.filter(search_data)

        if kwargs.get("catgeory", None):
            qs = kwargs["category"]

            query = query.filter(Q(category__name__icontains=qs) | Q(category__name__iexact=qs)).distinct()
        if kwargs.get("building", None):
            qs = kwargs["building"]

            query = query.filter(Q(building__name__icontains=qs) | Q(building__name__iexact=qs)).distinct()

        if kwargs.get("sort_by", None):
            qs = kwargs["sort_by"]
            is_asc = kwargs.get("is_asc", False)
            if not is_asc:
                qs = f"-{qs}"
            query = query.order_by(qs)
        return query

    def resolve_building(self, info, id):
        query = Product.objects.select_related("category").prefetch_related(
            "building_images","building_comments","building_requests"
                ).get(id=id)
        return query

class BuildingInput(graphene.InputObjectType):
    name = graphene.String()
    account_no = graphene.Int()
    dateCommissioned = graphene.Date()


class BuildingImageInput(graphene.InputObjectType):
    image_id = graphene.ID(required=True)
    is_cover = graphene.Boolean()

class CreateBuilding(graphene.Mutation):
    building = graphene.Field(BuildingType)

    class Arguments:
        building_data = BuildingInput(required=True)
        images = graphene.List(BuildingImageInput)
        total_count = graphene.Int(required=True)

    @is_authenticated
    def mutate(self, total_count, building_data, images, **kwargs):
        building = Building.objects.create(**building_data,**kwargs)

        BuildingImage.objects.bulk_create([
            BuildingImage(building_id = building.id, **image_data) for image_data in images
            ])

        return CreateBuilding(
                building=building
                )

class UpdateBuilding(graphene.Mutation):
    building = graphene.Field(BuildingType)

    class Arguments:
        building_data = BuildingInput()
        total_available = graphene.Int()
        building_id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, building_data, building_id, **kwargs):
        try:
            build_id = info.context.user.user_building.id
        except Exception:
            raise Exception("You do not habe a building to your name")

        if building_data.get("name", None):
            have_building = Building.objects.filter(building_id=build_id, name=building_data["name"])
            if have_building:
                raise Exception("you already have a building with this name.")

        Building.objects.filter(id = building_id).update(**building_data, **kwargs)

        return UpdateBuilding(
            building = Building.objects.get(id=building_id)
                )

class DeleteBuilding(graphene.Mutation):
    status = graphene.Boolean()
    class Arguments:
        building_id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, building_id):
        Building.objects.filter(id=buillding_id).delete()

        return DeleteBuilding(
            status = True
                )

class UpdateBuildingImage(graphene.Mutation):
    image = graphene.Field(BuildingImageType)
    class Arguments:
        image_data = BuildingImageInput()
        id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, image_data,id):
        try:
            build_id = info.context.user.user_building.id
        except Exception:
            raise Exception("you do not have a building , access denied.")

        my_image = BuildingImage.objects.filter(building_id=build_id, id=id)
        if not my_image:
            raise Exception("You do not own this building")
        my_image.update(**image_data)
        if image_data.get("is_cover", False):
            BuildingImage.objects.filter(building_id=build_id).exclude(id=id).update(is_cover=False)

        return UpdateBuildingImage(
            image = BuildingImage.objects.get(id=id)
                )

class CreateBuildingComment(graphene.Mutation):
    building_comment = graphene.Field(BuildingCommentType)

    class Arguments:
        building_id = graphene.ID(required=True)
        comment = graphene.String(required=True)
        rate = graphene.Int()

    @is_authenticated
    def mutate(self, info, building_id, **kwargs):
        user_build_id = None
        try:
            user_build_id = info.context.user.user_building.id
        except Exception:
            pass

        if user_build_id:
            own_build = Building.objects.filter(owner_id=user_build_id,id=building_id)
            if own_build:
                raise Exception("You cannot comment on your own building")

        BuildingComment.objects.filter(user=info.context.user.id, building_id=building_id).delete()

        bc = BuildingComment.objects.create(building_id=building_id, **kwargs)

        return CreateBuildingComment(
            building_comment = bc
                )


class Mutation(graphene.ObjectType):
    create_building = CreateBuilding.Field()
    update_building = UpdateBuilding.Field()
    delete_building = DeleteBuilding.Field()
    update_building_image = UpdateBuildingImage.Field()
    create_building_comment = CreateBuildingComment.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
