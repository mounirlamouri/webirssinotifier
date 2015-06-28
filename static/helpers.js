function getServiceWorkerRegistration() {
  if ('document' in self)
    return navigator.serviceWorker.getRegistration();
  return Promise.resolve(self.registration);
}

function getPushManager() {
  return getServiceWorkerRegistration().then(function(swRegistration) {
    return swRegistration.pushManager;
  });
}

function getPushSubscription() {
  return getPushManager().then(function(pushManager) {
    return pushManager.getSubscription();
  });
}

function getCurrentRegistrationId() {
  return getPushSubscription().then(function(subscription) {
    return subscription ? subscription.subscriptionId : "";
  });
}

function getMessages() {
  return getCurrentRegistrationId().then(function(registration_id) {
    console.log('found registration id');
    return fetch('/newmessages?registration_id=' + registration_id,
                 { mode: 'same-origin', credentials: 'include' });
  }).then(function(response) {
    if (response.status != '200')
      throw new Error();
    return response.json();
  }).then(function(json) {
    console.log('got json response');
    return json ? json.messages : [];
  });
}

function getRegistrations() {
  return fetch('/registrations', { mode: 'same-origin',
                                   credentials: 'include' }).then(function(r) {
    if (r.status != '200')
      throw new Error();
    return r.json();
  }).then(function(json) {
    return json ? json.registrations : [];
  });
}
