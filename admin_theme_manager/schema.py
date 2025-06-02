import graphene
from graphene_django import DjangoObjectType
from .models import AdminTheme

class AdminThemeType(DjangoObjectType):
    class Meta:
        model = AdminTheme
        fields = "__all__"

class SwitchAdminSkin(graphene.Mutation):
    class Arguments:
        theme_id = graphene.ID(required=True)

    Output = AdminThemeType

    @staticmethod
    def mutate(root, info, theme_id):
        user = info.context.user
        if not user.is_superuser:
            raise Exception("Permission denied.")
        try:
            theme = AdminTheme.objects.get(pk=theme_id)
        except AdminTheme.DoesNotExist:
            raise Exception("Theme not found.")
        theme.is_active = True
        theme.save()
        AdminTheme.objects.exclude(pk=theme_id).update(is_active=False)
        return theme

class Mutation(graphene.ObjectType):
    switch_admin_skin = SwitchAdminSkin.Field()

class Query(graphene.ObjectType):
    all_themes = graphene.List(AdminThemeType)
    active_theme = graphene.Field(AdminThemeType)

    def resolve_all_themes(root, info):
        return AdminTheme.objects.all()

    def resolve_active_theme(root, info):
        return AdminTheme.objects.filter(is_active=True).first()

schema = graphene.Schema(query=Query, mutation=Mutation)