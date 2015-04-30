import json
import webapp2
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import db

class Registration(db.Model):
  id = db.StringProperty(required=True)
  email = db.StringProperty(required=True)
  name = db.StringProperty()

class Message(db.Model):
  registration_id = db.StringProperty(required=True)
  text = db.StringProperty(required=True)
  channel = db.StringProperty()

#def clearRegistrations():
#  for r in db.GqlQuery("SELECT * FROM Registration"):
#    r.delete()

class SendHandler(webapp2.RequestHandler):
  def post(self):
    json_object = json.loads(self.request.body)

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

app = webapp2.WSGIApplication([
  ('/send', SendHandler),
], debug=True)