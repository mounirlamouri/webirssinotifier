importScripts('helpers.js');

self.addEventListener('push', function(event) {
  event.waitUntil(getMessages().then(function(messages) {
    var promises = [];
    messages.forEach(function(message) {
      if (!message.type)
        return;
      var title = '';
      switch (message.type) {
        case 'channel':
          title = 'New ping in ' + message.name;
          break;
        case 'query':
          title = 'New message from ' + message.name;
          break;
      }

      promises.push(self.registration.showNotification(title, {
        body: decodeURI(message.body),
        icon: '/images/200px-Irssi_logo.png',
      }));
    });
    return Promise.all(promises);
  }));
});
