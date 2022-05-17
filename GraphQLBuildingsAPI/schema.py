import graphene

from  BuildingsAPI.Buildings.schema import schema as building_schema
from  BuildingsAPI.Houses.schema    import schema as house_schema
from  BuildingsAPI.Payments.schema  import schema as payment_schema
from  BuildingsAPI.Users.schema     import schema as user_schema


class Query   (user_schema.Query, house_schema.Query, building_schema.Query, payment_schema.Query, graphene.ObjectType):
    pass


class Mutation(user_schema.Mutation, house_schema.Mutation, building_schema.Mutation, payment_schema.Mutation, graphene.ObjectType):
    pass 


schema  = graphene.Schema(query=Query, mutation=Mutation)
