function getCurrentRegistrationId() {
  return self.registration.pushManager.getSubscription().then(function(subscription) {
    return subscription ? subscription.subscriptionId : "";
  })
}

function getMessages() {
  return getCurrentRegistrationId().then(function(registration_id) {
    return fetch('https://webirssinotifier.appspot.com/newmessages?registration_id=' + registration_id).then(function(response) {
      if (response.status != '200')
        throw new Error();
      return response.json().then(function(json) {
        return json ? json.messages : [];
      });
    });
  });
}

self.addEventListener('push', function(event) {
  event.waitUntil(getMessages().then(function(messages) {
    messages.forEach(function(message) {
      var title = message.channel ? 'New ping in #' + message.channel
                                  : 'New private message';
      self.registration.showNotification(title, {
        body: message.text,
        icon: '/images/200px-Irssi_logo.png',
      });
    });
  }));
});
