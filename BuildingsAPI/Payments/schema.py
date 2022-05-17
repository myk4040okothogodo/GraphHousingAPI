import graphene
from graphene_django import DjangoObjectType
from GraphQLBuildingAPI.permissions import paginate, is_authenticated, get_query
from django.db.models import Q

from .models import (Category, Payment, PaymentImage )


class CategoryType(DjangoObjectType):
    count = graphene.Int()
    class Meta:
        model = Category
    def resolve_count(self, info):
        return self.payment_categories.count()

class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment

class PaymentImageType(DjangoObjectType):
    class Meta:
        model = PaymentImage


class Query(graphene.ObjectType):
    categories = graphene.List(CategoryType, name= graphene.String())
    payments   = graphene.Field(paginate(PaymentType), search=graphene.String(),
            max_amountpaid=graphene.Float(), min_amountpaid=graphene.Float(), building= graphene.String(), house= graphene.Int(), receipt_no= graphene.Int(), mine=graphene.Boolean())
    payment = graphene.Field(PaymentType, id=graphene.ID(required=True))

    def resolve_categories(self, info, name=False):
        query = Category.objects.prefetch_related("payment_categories")

        if name:
            query = query.filter(Q(name__icontains=name) | Q(name__iexact=name)).distinct()
        return query

    def resolve_payments(self, info, **kwargs):
        mine = kwargs.get("mine", False)
        if mine and not info.context.user:
            raise Exception("User auth required")

        query = Payment.objects.select_related("category","building","house").prefetch_related(
            "payment_images","payment_requests"
                )
        if mine:
            query = query.filter(house__user_id = info.context.user.id)

        if kwargs.get("search", None):
            qs = kwargs["search"]
            search_field = (
                "house","category__name","tenant","amountpaid"
                    )
            search_data = get_query(qs, search_fields)
            query = query.filter(search_data)

        if kwargs.get("min_amountpaid", None):
            qs = kwargs["min_amountpaid"]

            query = query.filter(Q(amountpaid__gt=qs) | Q(amountpaid=qs)).distinct()

        if kwargs.get("max_amountpaid", None):
            qs = kwargs["max_amountpaid"]

            query = query.filter(Q(amountpaid__lt=qs) | Q(amountpaid=qs)).distinct()

        if kwargs.get("category", None):
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

    def resolve_payment(self, info, id):
        query = Payment.objects.select_related("category","building","house").prefetch_related(
                "payment_images","payment_requests"
                ).get(id=id)
        return query


class PaymentInput(graphene.InputObjectType):
    amount = graphene.Float()
    receipt_no = graphene.Int()
    date = graphene.Date()
    category_id = graphene.ID()

class PaymentImageInput(graphene.InputObjectType):
    image_id = graphene.ID(required=True)
    is_cover = graphene.Boolean()

class CreatePayment(graphene.Mutation):
    payment = graphene.Field(PaymentType)

    class Arguments:
        payment_data = PaymentInput(required=True)
        images = graphene.List(PaymentImageInput)

    @is_authenticated
    def mutate(self, info, payment_data, images, **kwargs):
        try:
            house_id = info.context.user.user_house.id
            build_id = info.context.user.user_building.id
        except Exception:
            raise Exception("You are not authorized ")

        have_payment = Payment.objects.filter(house_id = house_id, receipt_no=payment_data["receipt_no"] )
        if have_payment:
            raise Exception("You have already made this payment")

        payment_data["house_id"] = house_id

        payment = Payment.objects.create(**payment_data, **kwargs)

        PaymentImage.objects.bulk_create([
            PaymentImage(payment_id=payment.id, **image_data) for image_data in images
            ])
        return CreatePayment(
                payment = payment
                )

class UpdatePayment(graphene.Mutation):
    payment = graphene.Field(PaymentType)

    class Arguments:
        payment_data = PaymentInput()
        payment_id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, payment_data, payment_id, **kwargs):
        try:
            house_id = info.context.user.user_house.id
        except Exception:
            raise Exception("you dont live in this house")

        if payment_data.get("receipt_no", None):
            have_payment = Payment.objects.filter(house_id=house_id, receipt_no=payment_data["receipt_no"])
            if have_payment:
                raise Exception("You already have a payment made with this receipt")

        Payment.objects.filter(id=payment_id, house_id=house_id).update(**payment_data, **kwargs)

        return UpdatePayment(
                payment = Payment.objects.get(id=payment_id)
                )

class DeletePayment(graphene.Mutation):
    status = graphene.Boolean()
    class Arguments:
        payment_id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, payment_id):
        Payment.objects.filter(id=payment_id, house_id=info.context.user.user_house.id).delete()

        return DeleteProduct(
                status = True
                )

class UpdatePaymentImage(graphene.Mutation):
    image = graphene.Field(PaymentImageType)

    class Arguments:
        image_data = PaymentImageInput()
        id = graphene.ID(required=True)

    @is_authenticated
    def mutate(self, info, image_data, id):
        try:
            house_id = info.context.user.user_house.id
        except Exception:
            raise Exception("You do not live in this house, access denied")

        my_image = PaymentImage.objects.filter(payment__house_id=house_id, id=id)
        if not my_image:
            raise Exception("You dont own this image")

        my_image.update(**image_data)
        if image_data.get("is_cover", False):
            PaymentImage.objects.filter(payment__house_id=house_id).exclude(id=id).update(is_cover=False)

        return UpdatePaymentImage(
            image = PaymentImage.objects.get(id=id)
        )


class Mutation(graphene.ObjectType):
    create_payment  = CreatePayment.Field()
    update_payment  = UpdatePayment.Field()
    delete_payment  = DeletePayment.Field()
    update_payment_image = UpdatePaymentImage.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)
