import graphene
from graphene_django import DjangoObjectType
from GraphQLBuildingsAPI.permissions import paginate, is_authenticated, get_query
from django.db.models import Q

from .models import (Category, House, HouseImage, HouseComment )


class CategoryType(DjangoObjectType):
    count = graphene.Int()
    class Meta:
        model = Category
    def resolve_count(self, info):
        return self.house_category.count()

class HouseType(DjangoObjectType):
    class Meta:
        model = House

class HouseImageType(DjangoObjectType):
    class Meta:
        model = HouseImage

class HouseCommentType(DjangoObjectType):
    class Meta:
        model = HouseComment


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType, name=graphene.String())
    houses   =  graphene.Field(paginate(HouseType), search= graphene.Int(),
            min_rent=graphene.Float(), max_rent=graphene.Float(), category=graphene.String(),
            building = graphene.String(), sort_by=graphene.String(), mine= graphene.Boolean())
    house =  graphene.Field(HouseType, id= graphene.ID(required=True))
            
    def resolve_categories(self, info, name= False):
        query = Category.objects.prefetch_related("house_categories")

        if name:
            query = query.filter(Q(name__icontains=name) | Q(name__iexact=name)).distinct()
        return query

    def resolve_houses(self, info, **kwargs):
        mine = kwargs.get("mine", False)
        if mine and not info.context.user:
            raise Exception("User authentication required")

        query = House.objects.select_related("category", "building").prefetch_related(
            "house_images", "house_comments","house_requests"
                )

        if mine:
            query = query.filter(building__user_id= info.context.user.id)

        if kwargs.get("search", None):
            qs = kwargs["search"]
            search_fields = (
                    "category__name","house_number","rent","tenant","occupied"
                    )
            search_data = get_query(qs, search_fields)
            query = query.filter(search_data)

        if kwargs.get("min_rent", None):
            qs = kwargs["min_rent"]

            query = query.filter(Q(rent__gt=qs) | Q(rent=qs)).distinct()
        if kwargs.get("max_price", None):
            qs = kwargs["max_rent"]

            query = query.filter(Q(rent__lt=qs) | Q(rent=qs)).distinct()

        if kwargs.get("category", None):
            qs = kwargs["category"]

            query = query.filter(Q(category__name__icontains=qs)
                    | Q(category__name__iexact=qs)
                    ).distinct()

        if kwargs.get("building", None):
            qs = kwargs["building"]

            query = query.filter(Q(building__name__icontains=qs)
            | Q (building__name__iexact=qs)
                    ).distinct()

        if kwargs.get("sort_by", None):
            qs = kwargs["sort_by"]

            is_asc = kwargs.get("is_asc", False)
            if not is_asc:
                qs = f"-{qs}"
            query =  query.order_by(qs)

        return query

    def resolve_house(self, info, id):
        query = House.objects.select_related("category", "building").prefetch_related(
            "house_images","house_comments","house_requests"
                ).get(id=id)
        return query


class HouseInput(graphene.InputObjectType):
    house_number = graphene.Int()
    rent         = graphene.Float()
    floor_no     = graphene.Int()
    occupied     = graphene.Boolean()

class HouseImageInput(graphene.InputObjectType):
    image_id = graphene.ID(required=True)
    is_cover = graphene.Boolean()

class CreateHouse(graphene.Mutation):
    house = graphene.Field(HouseType)
    class Arguments:
        house_data = HouseInput(required=True)
        images  = graphene.List(HouseImageInput)

    @is_authenticated
    def mutate(self, info, house_data, images, **kwargs):
        try:
            build_id = info.context.user.user_building.id
        except Exception:
            raise Exception("You do not have a building")

        have_house = House.objects.filter(building_id=build_id, house_number=house_data["house_number"])
        if have_house:
            raise Exception("You already have a house with this number")

        house_data["building_id"] = build_id

        house = House.objects.create(**house_data, **kwargs)

        HouseImage.objects.bulk_create([
            HouseImage(house_id=house.id, **image_data) for image_data in images
            ])

        return CreateHouse(
                house=house
                )

class UpdateHouse(graphene.Mutation):
    house = graphene.Field(HouseType)

    class Arguments:
        house_data = HouseInput()
        house_id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, house_data, house_id, **kwargs):
        try:
            build_id = info.context.user.user_building.id
        except Exception:
            raise Exception("You do not own a building")

        if house_data.get("house_number", None):
            have_house = House.objects.filter(building_id=build_id, house_number=house_data["house_number"])
            if have_house:
                raise Exception("You already have a house with this number")

        House.objects.filter(id=house_id, building_id=build_id).update(**house_data, **kwargs)
        return UpdateHouse(
                    house =House.objects.get(id=house_id)
                    )

class  DeleteHouse(graphene.Mutation):
    status = graphene.Boolean()

    class Arguments:
        house_id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self,info, house_id):
        House.objects.filter(id=house_id, building_id=info.context.user.user_building.id).delete()

        return DeleteHouse(
                status = True
                )

class UpdateHouseImage(graphene.Mutation):
    image = graphene.Field(HouseImageType)

    class Arguments:
        image_data = HouseImageInput()
        id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, image_data, id):
        try:
            build_id = info.context.user.user_building_id
        except Exception:
            raise Exception("You do not have a house, access denied")

        my_image = HouseImage.objects.filter(house__building_id=build_id, id=id)
        if not my_image:
            raise Exception("You do not own this house")
        my_image.update(**image_data)
        if image_data.get("is_cover", False):
            HouseImage.objects.filter(house__building_id=build_id).exclude(id=id).update(is_cover=False)

        return UpdateHouseImage(
            image = HouseImage.objects.get(id = id)
        )    

class CreateHouseComment(graphene.Mutation):
    house_comment = graphene.Field(HouseCommentType)

    class Arguments:
        house_id = graphene.ID(required=True)
        comment = graphene.String(required=True)
        rate = graphene.Int()

    @is_authenticated
    def mutate(self, info, house_id, **kwargs):
        user_build_id = None
        try:
            user_build_id = info.context.user.user_building.id
        except Exception:
            pass

        if user_build_id:
            own_house = House.objects.filter(building_id= user_build_id, id=house_id)
            if own_house:
                raise Exception("you cannot commment on your own houses conditions")
        HouseComment.objects.filter(user= info.context.user.id, house_id=house_id).delete()

        hc = HouseComment.objects.create(house_id=house_id, **kwargs)
        return CreateHouseComment(
            house_comment = hc
                )


class Mutation(graphene.ObjectType):
    create_house = CreateHouse.Field()
    update_house = UpdateHouse.Field()
    delete_house = DeleteHouse.Field()
    update_house_image = UpdateHouseImage.Field()
    create_house_comment = CreateHouseComment.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
