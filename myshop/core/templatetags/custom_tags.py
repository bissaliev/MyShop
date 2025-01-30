from django.http.request import QueryDict
from django.template import Library
from django.template.context import RequestContext
from shop.models import Category

register = Library()


@register.filter
def addclass(tag, css):
    return tag.as_widget(attrs={"class": css})


@register.simple_tag
def get_categories():
    return Category.objects.all()


@register.simple_tag(takes_context=True)
def query_string(context):
    request: RequestContext = context["request"]
    query: QueryDict = request.GET.copy()
    for q in query:
        print(q)
    if "page" in query:
        del query["page"]
    return query.urlencode()
