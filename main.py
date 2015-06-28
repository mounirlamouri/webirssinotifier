import json
import os
import urllib
import webapp2

from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Registration(db.Model):
  id = db.StringProperty(required=True)
  user = db.StringProperty(required=True)
  name = db.StringProperty()

class Message(db.Model):
  registration_id = db.StringProperty(required=True)
  type = db.StringProperty(required=True) # TODO: use enum?
  name = db.StringProperty(required=True)
  body = db.StringProperty(required=True)

class MainHandler(webapp2.RequestHandler):
  def get(self):
    user = ""
    if users.get_current_user():
      user = users.get_current_user().nickname()

    login_logout_url = ""
    if user:
      login_logout_url = users.create_logout_url('/')
    else:
      login_logout_url = users.create_login_url('/')

    template_values = {
      'user': user,
      'login_logout_url': login_logout_url,
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class SendHandler(webapp2.RequestHandler):
  def post(self):
    try:
      json_object = json.loads(self.request.body)
    except:
      self.response.write('{ "success": false, "error": "ParsingError", "body": "' + self.request.body + '" }');
      return

    for registration in db.GqlQuery("SELECT * FROM Registration WHERE user = :1", json_object['user']):
      msg = Message(registration_id=registration.id,
                    type=json_object['type'],
                    name=json_object['name'],
                    body=json_object['body'])
      msg.put()

      form_fields = {
        "registration_id": registration.id,
        "data": {
          "type": json_object['type'],
          "name": json_object['name'],
          "body": json_object['body'],
        },
      }
      form_data = urllib.urlencode(form_fields)
      result = urlfetch.fetch(url="https://android.googleapis.com/gcm/send",
                              payload=form_data,
                              method=urlfetch.POST,
                              headers={
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Authorization': 'key=AIzaSyDn9hiUO1LyVJFxKA5u2qMCYox4NZ5vjdM'
              })

    self.response.write('{ "success": true }');

class NewMessagesHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.response.write('{ "success": false, "error": "LoginError" }');
      return

    registration_id = self.request.get('registration_id')

    # Check that the registration is owned by the user.
    if db.GqlQuery("SELECT * FROM Registration WHERE id = :1 AND user = :2",
                   registration_id, user.nickname()).count() == 0:
      self.response.write('{ "success": false, "error": "RegistrationNotFound" }');
      return

    messages = []
    for message in db.GqlQuery("SELECT * FROM Message WHERE registration_id = :1",
                               registration_id):
      messages.append({
        'type': message.type,
        'name': message.name,
        'body': message.body
      })

      # It was sent back, remove from storage.
      message.delete()

    self.response.write('{ "messages": ' + json.dumps(messages) + ' }');

class GetRegistrationsHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.response.write('{ "success": false, "error": "LoginError" }');
      return

    registrations = []
    for registration in db.GqlQuery("SELECT * FROM Registration WHERE user = :1", user.nickname()):
      registration = {
        'id': registration.id,
        'name': registration.name
      }
      registrations.append(registration)

    self.response.write('{ "registrations": ' + json.dumps(registrations) + ' }');

class RegisterHandler(webapp2.RequestHandler):
  def post(self):
    try:
      json_object = json.loads(self.request.body)
    except:
      self.response.write('{ "success": false, "error": "ParsingError", "body": "' + self.request.body + '" }');
      return

    user = users.get_current_user()
    if not user:
      self.response('{ "success": false, "error": "LoginError" }');
      return

    if db.GqlQuery("SELECT * FROM Registration WHERE user = :1 AND id = :2",
                   user.nickname(), json_object['id']).count() != 0:
      self.response.write('{ "success": true }');
      return

    registration = Registration(id=json_object['id'],
                                user=user.nickname(),
                                name=json_object['name'])
    registration.put()
    self.response.write('{ "success": true }');

class UnregisterHandler(webapp2.RequestHandler):
  def post(self):
    try:
      json_object = json.loads(self.request.body)
    except:
      self.response.write('{ "success": false, "error": "ParsingError", "body": "' + self.request.body + '" }');
      return

    user = users.get_current_user()
    if not user:
      self.response('{ "success": false, "error": "LoginError" }');
      return

    for registration in db.GqlQuery("SELECT * FROM Registration WHERE user = :1 AND id = :2",
                                    user.nickname(), json_object['id']):
      registration.delete()

    self.response.write('{ "success": true }');

app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/send', SendHandler),
  ('/newmessages', NewMessagesHandler),
  ('/registrations', GetRegistrationsHandler),
  ('/register', RegisterHandler),
  ('/unregister', UnregisterHandler),
], debug=True)
