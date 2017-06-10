import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hsysi.settings")
from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import logging
import tornado.httpserver
from tornado.httpclient import HTTPError
from httpclient_session import Session
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.wsgi
from importlib import import_module
from django.conf.urls import url
from tornado import template 
import time

if django.VERSION[1] > 5:
    django.setup()
    
define('port', type=int, default=8080)
tornado.options.parse_command_line()

from identity.panels import *
from identity.models import *
from identity.access import *
from identity.flakes import *

#https://gist.github.com/654157
#https://thinkfaster.co/2015/01/run-django-on-tornado/
class PulseHandler(tornado.web.RequestHandler):
    def get_django_session(self):
        if not hasattr(self, '_session'):
            engine = import_module(django.conf.settings.SESSION_ENGINE)
            session_key = self.get_cookie(django.conf.settings.SESSION_COOKIE_NAME)
            self._session = engine.SessionStore(session_key)
            return self._session

    def get_current_user(self):
        # get_user needs a django request object, but only looks at the session
        class Dummy(object): pass
        django_request = Dummy()
        django_request.session = self.get_django_session()
        user = django.contrib.auth.get_user(django_request)
        if user.is_authenticated():
            return user
        else:
            # try basic auth
            headers = self.request.headers
            basic_authorization = False
            try:
                basic_authorization = headers.has_key('Authorization')
            except:
                basic_authorization = headers._dict.has_key('Authorization')
            if not basic_authorization:
                return None
            kind, data = self.request.headers['Authorization'].split(' ')
            if kind != 'Basic':
                return None
            (username, _, password) = data.decode('base64').partition(':')
            user = django.contrib.auth.authenticate(username = username, password = password)
            if user is not None and user.is_authenticated():
                return user
            return None
    
    def get_django_request(self):
        request = django.core.handlers.wsgi.WSGIRequest(tornado.wsgi.WSGIContainer.environ(self.request))
        request.session = self.get_django_session()    
        if self.current_user:
            request.user = self.current_user
        else:
            request.user = django.contrib.auth.models.AnonymousUser()
        return request

class TasksPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, admission_id, last_id):
        def push(tasks, request, vewer):
            content = TasksFlake(request, viewer, tasks)
            latest_id = tasks.latest('id').id
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(''.join(content._container))
            self.finish()
        def timeout():
            self.write('')
            self.finish()
        def poll(request, admission, viewer, counter=10):
            logging.warn(counter)
            if counter:
                tasks = Task.objects.filter(admission=admission, id__gt = last_id)
                if len(tasks) > 0: push(tasks, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, admission, viewer, counter-1))
            else: timeout()
        
        viewer = self.current_user
        if viewer is None:
            return None
        
        request   = self.get_django_request()
        admission = Admission.objects.get(pk=admission_id)
        poll(request, admission, viewer)
        
class WatchPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, admission_id, last_id):
        def push(activities, request, vewer):
            latest_id = activities.latest('id').id
            multiset = {}
            for a in activities:
                if a.task.id in multiset:
                    multiset[a.task.id].append(a.id)
                else:
                    multiset[a.task.id] = [a.id]

            response = {
                'admission': admission_id,
                'update':    multiset
            }
            
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(response)
            self.finish()
            print(response)
        def timeout():
            self.write('')
            self.finish()
        def poll(request, admission, viewer, counter=10):
            if counter:
                activities = Activity.objects.filter(task__admission=admission, id__gt = last_id)
                if len(activities) > 0: push(activities, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, admission, viewer, counter-1))
            else: timeout()
        
        viewer = self.current_user
        if viewer is None:
            return None
        
        request   = self.get_django_request()
        admission = Admission.objects.get(pk=admission_id)
        poll(request, admission, viewer)


class ActivitiesPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, task_id, last_id):
        def push(activities, request, vewer):
            content = ActivitiesFlake(request, viewer, activities)
            latest_id = activities.latest('id').id
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(''.join(content._container))
            self.finish()
        def timeout():
            self.write('')
            self.finish()
        def poll(request, task, viewer, counter=10):
            if counter:
                activities = Activities.objects.filter(task=task, id__gt = last_id)
                if len(activities) > 0: push(activities, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, task, viewer, counter-1))
            else: timeout()
        
        viewer = self.current_user
        if viewer is None:
            return None
        
        request = self.get_django_request()
        task    = Task.objects.get(pk=task_id)
        poll(request, task, viewer)
        
class StoriesPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, owner_id, last_id):
        def push(stories, request, vewer):
            content = StoriesFlake(request, viewer, stories)
            latest_id = stories.latest('id').id
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(''.join(content._container))
            self.finish()
        def timeout():
            self.write('')
            self.finish()
        def poll(request, owner, viewer, counter=10):
            if counter:
                stories = StoryAccess().all(viewer, owner, last_id)
                if len(stories) > 0: push(stories, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, owner, viewer, counter-1))
            else: timeout()
        
        viewer = self.current_user
        if viewer is None:
            return None
        
        request = self.get_django_request()
        owner   = HmsUser.objects.get(pk=owner_id).real()
        poll(request, owner, viewer)
        
class AdmissionsPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, owner_id, last_id):
        def push(admissions, request, vewer):
            content = AdmissionsFlake(request, viewer, admissions)
            try:
                latest_id = admissions.latest('id').id
            except AttributeError:
                print(len(admissions))
                if len(admissions) > 0:
                    latest_id = admissions[0].id
                else:
                    latest_id = 0
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(''.join(content._container))
            self.finish()
        def timeout():
            self.write('')
            self.finish()
        def poll(request, owner, viewer, counter=10):
            if counter:
                admissions = AdmissionAccess().all(viewer, owner, last_id)
                if len(admissions) > 0: push(admissions, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, owner, viewer, counter-1))
            else: timeout()
        
        viewer = self.current_user
        if viewer is None:
            return None
        
        request = self.get_django_request()
        owner   = HmsUser.objects.get(pk=owner_id).real()
        poll(request, owner, viewer)
        
class AppointmentsPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, owner_id, last_id):
        def push(appointments, request, vewer):
            content = AppointmentsFlake(request, viewer, appointments)
            latest_id = appointments.latest('id').id
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(''.join(content._container))
            self.finish()
        def timeout():
            self.write('')
            self.finish()
        def poll(request, owner, viewer, counter=10):
            if counter:
                appointments = AppointmentAccess().all(viewer, owner, last_id)
                if len(appointments) > 0: push(appointments, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, owner, viewer, counter-1))
            else: timeout()
        
        viewer = self.current_user
        if viewer is None:
            return None
        
        request = self.get_django_request()
        owner   = HmsUser.objects.get(pk=owner_id).real()
        poll(request, owner, viewer)

class TalkPulseHandler(PulseHandler):
    def get(self):
        self.render("talk.html")

# one uer can chat with multiple users at the same time
# the user with whom the user is chating is owner_id (the other party)
# Different channels will be created for different one-to-one chat sessions
# id of the other end is provided in owner_id in GET request
# last_id is the id of the last message recieved in that one-to-one channel
class ChatPulseHandler(PulseHandler):
    @tornado.web.asynchronous
    def get(self, owner_id, last_id):
        def push(messages, request, viewer):
            content = MessagesFlake(request, viewer, messages)
            latest_id = messages.latest('id').id
            self.set_header('Access-Control-Expose-Headers', 'Last-Id')
            self.set_header('Last-Id', latest_id)
            self.write(''.join(content._container))
            self.finish()
        def timeout():
            self.write('')
            self.finish()
        def poll(request, owner, viewer, counter=10):
            if counter:
                messages = MessageAccess().all(viewer, owner, last_id)
                if len(messages) > 0: push(messages, request, viewer)
                else:
                    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2, lambda: poll(request, owner, viewer, counter-1))
            else: timeout()

        viewer = self.current_user
        if viewer is None:
            return None
        
        request = self.get_django_request()
        owner   = HmsUser.objects.get(pk=owner_id).real()
        poll(request, owner, viewer)

clients = {}
class TalkWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        socket_id = len(clients)
        self.id = socket_id
        clients[socket_id] = self
    def on_close(self):
        if self.id in clients:
            del clients[self.id]
    def on_message(self, message):
        print(message)
        for c in clients:
            client = clients[c]
            if client != self:
                client.write_message(message)
            

class NoCacheStaticHandler(tornado.web.StaticFileHandler):
	pass

def main(): 
    logger = logging.getLogger(__name__)
    wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
    tornado_app = tornado.web.Application([
            (r'^/pulse/tasks/(?P<admission_id>\d+)/(?P<last_id>\d+)$',      TasksPulseHandler),
            (r'^/pulse/activities/(?P<task_id>\d+)/(?P<last_id>\d+)$',      ActivitiesPulseHandler),
            (r'^/pulse/watch/(?P<admission_id>\d+)/(?P<last_id>\d+)$',      WatchPulseHandler), # watch activities of all activities of all tasks of an admission
            (r'^/pulse/stories/(?P<owner_id>\d+)/(?P<last_id>\d+)$',        StoriesPulseHandler),
            (r'^/pulse/admissions/(?P<owner_id>\d+)/(?P<last_id>\d+)$',     AdmissionsPulseHandler),
            (r'^/pulse/appointments/(?P<owner_id>\d+)/(?P<last_id>\d+)$',   AppointmentsPulseHandler),
            (r'^/pulse/talk/?$',   TalkPulseHandler),
            (r'^/pulse/chat/(?P<owner_id>\d+)/(?P<last_id>\d+)$',           ChatPulseHandler),
            (r'^/pulse/talksock/?$',   TalkWebSocket),
            (r'/static/(.*)', NoCacheStaticHandler, {'path': 'identity/static'}),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ], debug=True)
    logger.info("Tornado server starting...")
    server = tornado.httpserver.HTTPServer(tornado_app, ssl_options={
        "certfile": "/home/sensiaas/projects/hsys/hkeys/cert.pem",
        "keyfile": "/home/sensiaas/projects/hsys/hkeys/key.pem",
    })
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
 
if __name__ == '__main__':
    main()
