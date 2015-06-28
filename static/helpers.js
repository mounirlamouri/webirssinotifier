function getServiceWorkerRegistration() {
  if ('document' in self)
    return navigator.serviceWorker.getRegistration();
  return Promise.resolve(self.registration);
}

function getCurrentRegistrationId() {
  return getServiceWorkerRegistration().then(function(swRegistration) {
    return swRegistration.pushManager.getSubscription();
  }).then(function(subscription) {
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

function register(id, name) {
  return fetch('/register', { mode: 'same-origin',
                              method: 'post',
                              credentials: 'include',
                              body: JSON.stringify({ id: id, name: name }) }).then(function(r) {
    if (r.status != '200')
      throw new Error();
    return r.json();
  }).then(function(json) {
    if (!json || !json.success)
      throw new Error();
  });
}
