import graphene
import django_filters
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Link, Vote


class LinkFilter(django_filters.FilterSet):
    """
    Relay allows you to use django-filter for filtering data.
    Here, you’ve defined a FilterSet, with the url and description fields.
    """
    class Meta:
        model = Link
        fields = ['url', 'description']


class LinkNode(DjangoObjectType):
    """
    The data is exposed in Nodes, so you must create one for the links.
    """
    class Meta:
        """
        Each node implements an interface with an unique ID (you’ll see the result of this in a bit).
        """
        model = Link
        interfaces = (graphene.relay.Node, )


class VoteNode(DjangoObjectType):
    class Meta:
        model = Vote
        interfaces = (graphene.relay.Node,)


class RelayQuery(graphene.ObjectType):
    """
    Uses the LinkNode with the relay_link field inside your new query.
    Defines the relay_links field as a Connection, which implements the pagination structure.
    - Edges and Nodes: they’re the main structure of Relay. Edges represents a collection,
    which has pagination properties. Nodes are the final object or an edge for a new list of objects.
    - The IDs are now a global unique base64 encoded string.

    What about the pagination? Each field has some arguments for controlling it: before, after, first and last.
    On top of that, each edge has a pageInfo object, including the cursor for navigating between pages.

    The first: 1 parameter limits the response for the first result. You also requested the pageInfo,
    which returned the navigation cursors.

    E.g. with first: 1, after:"YXJyYXljb25uZWN0aW9uOjA=" the response returned is the first one after the last link.
    """
    relay_link = graphene.relay.Node.Field(LinkNode)
    relay_links = DjangoFilterConnectionField(LinkNode, filterset_class=LinkFilter)


class RelayCreateLink(graphene.relay.ClientIDMutation):
    link = graphene.Field(LinkNode)

    class Input:
        url = graphene.String()
        description = graphene.String()

    def mutate_and_get_payload(root, info, **input):
        user = info.context.user or None

        link = Link(
            url=input.get('url'),
            description=input.get('description'),
            posted_by=user,
        )
        link.save()

        return RelayCreateLink(link=link)


class RelayMutation(graphene.AbstractType):
    relay_create_link = RelayCreateLink.Field()
