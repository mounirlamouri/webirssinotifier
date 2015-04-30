self.addEventListener('push', function(event) {
  self.registration.showNotification('IRC ping', {
    body: 'Someone tries to reach you.',
    icon: '/images/200px-Irssi_logo.png',
  });
});
