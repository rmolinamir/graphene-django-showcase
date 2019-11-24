import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType

from django.db.models import Q
from users.schema import UserType
from .models import Link, Vote


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class LinkType(DjangoObjectType):
    class Meta:
        model = Link
    votes = graphene.AbstractType()
    vote_count = graphene.Int() 

    def resolve_votes(self, info):
        """
        Resolves the number of (up)votes of this link
        """
        return Link.objects.get(pk=self.id).votes

    def resolve_vote_count(self, info):
        """
        Resolves the number of (up)votes of this link
        """
        return Link.objects.get(pk=self.id).votes.count()


class Query(graphene.ObjectType):
    links = graphene.List(
        LinkType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        """
        Resolves links in the database depending on the parameters.
        :param search: Filters by URL or description.
        :param first: Selects the first N number of links.
        :param skip: Skips the first N number of links
        :return: Links List.
        """
        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = Link.objects.filter(filter)
        else:
            qs = Link.objects.all()
        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]
        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class CreateLink(graphene.Mutation):
    """
    Defines a mutation class. Right after, you define the output of the mutation, the data the server can send back
    to the client. The output is defined field by field for learning purposes. In the next mutation you’ll
    define them as just one.
    """
    id = graphene.ID()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    """
    Defines the data you can send to the server, in this case, the links’ url and description.
    """
    class Arguments:
        url = graphene.String()
        description = graphene.String()

    """
    The mutation method: it creates a link in the database using the data sent by the user, through the url and
    description parameters. After, the server returns the CreateLink class with the data just created. See how
    this matches the parameters set on #1.
    """
    def mutate(self, info, url, description):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged in to vote!')
        link = Link(
            url=url,
            description=description,
            posted_by=user,
        )
        link.save()
        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )


class CreateVote(graphene.Mutation):
    """
    CreateVote mutation type root field.
    """
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.ID()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('You must be logged in to vote!')
        link = Link.objects.get(pk=link_id)
        if not link:
            raise Exception('Invalid link!')
        vote = Vote.objects.filter(link=link_id, user=user).first()
        if vote:
            raise Exception('User already voted!')
        Vote.objects.create(
            user=user,
            link=link,
        )
        return CreateVote(user=user, link=link)


class Mutation(graphene.ObjectType):
    """
    Creates a mutation class with a field to be resolved, which points to our mutation defined before.
    """
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
