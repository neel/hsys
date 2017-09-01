from django import template
from hsysi.utils import *
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.conf import settings
from django.core import urlresolvers
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from identity.utils.symptoms import builder, decorator
try:
    from django.utils import simplejson as sjson
except:
    import simplejson as sjson

register = template.Library()

register.filter('delta_string', delta_string)

class ViewNode(Node):
    def __init__(self, url_or_view, args, kwargs):
        self.url_or_view = url_or_view
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        if 'request' not in context:
            return ""
        request = context['request']

        url_or_view = Variable(self.url_or_view).resolve(context)
        try:
            urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
            resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
            view, args, kwargs = resolver.resolve(url_or_view)
        except:
            view = urlresolvers.get_callable(url_or_view)
            args = [Variable(arg).resolve(context) for arg in self.args]
            kwargs = {}
            for key, value in self.kwargs.items():
                kwargs[key] = Variable(value).resolve(context)

        try:
            if callable(view):
                return view(context['request'], *args, **kwargs).content
            raise "%r is not callable" % view
        except:
            if settings.TEMPLATE_DEBUG:
                raise
        return ""


def do_view(parser, token):
    """
    Inserts the output of a view, using fully qualified view name (and then some
    args), a or local Django URL.

     {% view view_or_url arg[ arg2] k=v [k2=v2...] %}

    This might be helpful if you are trying to do 'on-server' AJAX of page
    panels. Most browsers can call back to the server to get panels of content
    asynchonously, whilst others (such as mobiles that don't support AJAX very
    well) can have a template that embeds the output of the URL synchronously
    into the main page. Yay! Go the mobile web!

    Follow standard templatetag instructions for installing.

    IMPORTANT: the calling template must receive a context variable called
    'request' containing the original HttpRequest. This means you should be OK
    with permissions and other session state.

    ALSO NOTE: that middleware is not invoked on this 'inner' view.

    Example usage...

    Using a view name (or something that evaluates to a view name):
     {% view "mymodule.views.inner" "value" %}
     {% view "mymodule.views.inner" keyword="value" %}
     {% view "mymodule.views.inner" arg_expr %}
     {% view "mymodule.views.inner" keyword=arg_expr %}
     {% view view_expr "value" %}
     {% view view_expr keyword="value" %}
     {% view view_expr arg_expr %}
     {% view view_expr keyword=arg_expr %}

    Using a URL (or something that evaluates to a URL):
     {% view "/inner" %}
     {% view url_expr %}


    (Note that every argument will be evaluated against context except for the
    names of any keyword arguments. If you're warped enough to need evaluated
    keyword names, then you're probably smart enough to add this yourself!)

    """

    args = []
    kwargs = {}
    tokens = token.split_contents()
    if len(tokens)<2:
        raise TemplateSyntaxError, ("%r tag requires one or more arguments" %
                                    token.contents.split()[0])
    tag_name = tokens.pop(0)
    url_or_view = tokens.pop(0)
    for token in tokens:
        equals = token.find("=")
        if equals == -1:
            args.append(token)
        else:
            kwargs[str(token[:equals])] = token[equals+1:]
    return ViewNode(url_or_view, args, kwargs)

register.tag('view', do_view)

@register.filter(name='lookup')
def cut(value, arg):
    return value[arg]

@register.filter(name='classname')
def classname(obj):
    classname = obj.__class__.__name__
    return classname

@register.filter(name='usertype')
def usertype(u):
    if u.__class__.__name__ == 'AnonymousUser':
        return 'Anonymous'
    return classname(u.real())

@register.filter(name='jsonify')
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return sjson.dumps(object)

def show_value_na(value):
    if value.lower().strip() == "n/a":
        return "<span class='value-na'>"+value+"</span>"
    return value

@register.filter(name='complaint_symptoms')
def complaint_symptoms(obj):
    b = builder()
    sub = b.subtree(obj)
    return decorator().decorate(sub, "en")

@register.filter(name='complaint_vitals')
def complaint_vitals(obj):
    html = "<div class='vitals-container'>"
    for type in obj:
        value = obj[type]
        html += "<div class='vital'>"
        html += "<div class='complaint-category vital-category'>"+type+"</div>"
        html += "<div class='complaint-vital vital-value'>"
        try:
            d = value+1
            html += str(value)
        except TypeError:
            html += value
        html += "</div>"
        html += "</div>"
    html += "</div>"
    return html

@register.filter(name='complaint_symptoms_summarized')
def complaint_symptoms_summarized(obj):
    return complaint_symptoms(obj)

@register.filter(name='complaint_observations')
def complaint_observations(obj):
    html = "<div class='observations-container'>"
    for observation in obj:
        html += "<div class='observation'>"
        html += observation
        html += "</div>"
    html += "</div>"
    return html

@register.filter(name='complaint_habits')
def complaint_habits(obj):
    html = "<div class='habits-container'>"
    for observation in obj:
        html += "<div class='habit'>"
        html += observation
        html += "</div>"
    html += "</div>"
    return html

@register.filter(name='complaint_history')
def complaint_history(obj):
    html = "<div class='history-container'>"
    for observation in obj:
        html += "<div class='history'>"
        html += observation
        html += "</div>"
    html += "</div>"
    return html

@register.filter(name='complaint_postexams')
def complaint_postexams(obj):
    html = "<div class='postexams-container'>"
    for k1 in obj:
        v1 = obj[k1]
        html += "<div class='postexam'>"
        html += "<h3 class='complaint-category postexam-category'>"+k1+"</h3>"
        html += "<div class='complaint-questionnaires postexam-questionnaires'>"
        for k2 in v1:
            v2 = v1[k2]
            html += "<div class='complaint-qa postexam-qa'><span class='complaint-question postexam-question'>"+k2+"</span><span class='complaint-answer postexam-answer'>"+ show_value_na(v2) +"</span></div>"
        html += "</div>"
        html += "</div>"
    html += "</div>"
    return html

@register.filter(name='complaint_postexams_summarized')
def complaint_postexams_summarized(obj):
    html = "<div class='postexams-container'>"
    for k1 in obj:
        v1 = obj[k1]
        html += "<div class='postexam'>"
        html += "<h3 class='complaint-category postexam-category'>"+k1+"</h3>"
        html += "<div class='complaint-questionnaires postexam-questionnaires'>"
        for k2 in v1:
            v2 = v1[k2]
            if v2.strip().lower() != "n/a":
                html += "<div class='complaint-qa postexam-qa'><span class='complaint-question postexam-question'>"+k2+"</span><span class='complaint-answer postexam-answer'>"+ show_value_na(v2) +"</span></div>"
        html += "</div>"
        html += "</div>"
    html += "</div>"
    return html


@register.filter(name='complaint_family')
def complaint_family(obj):
    html = "<div class='family-container'>"
    for relation in obj:
        value = obj[relation]
        html += "<div class='family'>"
        html += "<h3 class='complaint-category family-category'>"+relation+"("+str(len(value['history']))+")"+"</h3>"
        html += "<div class='complaint-questionnaires family-questionnaires'>"
        for history in value['history']:
            html += "<div class='complaint-qa family-qa'><span class='complaint-question family-question'>"+history+"</span></div>"
        html += "</div>"
        html += "</div>"
    html += "</div>"
    return html

@register.filter(name='complaint_family_summarized')
def complaint_family_summarized(obj):
    html = "<div class='family-container'>"
    for relation in obj:
        value = obj[relation]
        if len(value['history']) > 0:
            html += "<div class='family'>"
            html += "<div class='complaint-category family-category'>"+relation+"</div>"
            html += "<div class='complaint-questionnaires family-questionnaires'>"
            for history in value['history']:
                html += "<span class='complaint-qa family-qa'><span class='complaint-question family-question'>"+history+"</span></span>"
            html += "</div>"
            html += "</div>"
    html += "</div>"
    return html