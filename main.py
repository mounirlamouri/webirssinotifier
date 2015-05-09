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
  text = db.StringProperty(required=True)
  channel = db.StringProperty()

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

    msg = Message(registration_id=json_object['registration_id'],
                  text=json_object['text'],
                  channel=json_object['channel'])
    msg.put()

    form_fields = {
      "registration_id": json_object['registration_id'],
      "data": {
        "text": json_object['text'],
        "channel": json_object['channel'],
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

    # TODO: check that the user owns the given registration_id.

    messages = []
    for message in db.GqlQuery("SELECT * FROM Message WHERE registration_id = :1",
                               self.request.get('registration_id')):
      message_field = {
        'text': message.text
      }
      if message.channel:
        message_field['channel'] = message.channel
      messages.append(message_field)

      # It was sent back, remove from storage.
      message.delete()

    self.response.write('{ "messages": ' + json.dumps(messages) + ' }');

app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/send', SendHandler),
  ('/newmessages', NewMessagesHandler),
], debug=True)
