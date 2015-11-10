// Requires helpers.js to be loaded.

function register(name) {
  getPushManager().then(function(pushManager) {
    return pushManager.subscribe({ userVisibleOnly: true });
  }).then(function(subscription) {
    var id = subscription.subscriptionId;
    console.log(id);
    return fetch('/register', { mode: 'same-origin',
                                method: 'post',
                                credentials: 'include',
                                body: JSON.stringify({ id: id, name: name }) });
  }).then(function(response) {
    if (response.status != '200')
      throw new Error();
    return response.json();
  }).then(function(json) {
    if (!json || !json.success)
      throw new Error();
  }).then(refreshUI);
}

function unregister() {
  var subscription;
  getPushSubscription().then(function(s) {
    subscription = s;
    if (!subscription)
      throw new Error();
    var id = subscription.subscriptionId;
    return fetch('/unregister',
                 { mode: 'same-origin', method: 'post', credentials: 'include',
                   body: JSON.stringify({ id: id }) });
  }).then(function(response) {
    if (response.status != '200')
      throw new Error();
    return subscription.unsubscribe();
  }).then(refreshUI);
}

function createDeviceInfo(name, id) {
  var container = document.createElement('div');
  container.id = id;

  var txt = document.createElement('input');
  txt.type = 'text';
  txt.readOnly = true;
  txt.value = name;
  container.appendChild(txt);

  var button = document.createElement('input');
  button.type = 'button';
  button.value = 'Unregister';
  button.onclick = function() {
    unregister();
  };
  container.appendChild(button);

  return container;
}

function createSubscriptionForm() {
  var form = document.createElement('form');
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    register(this.name.value);
  });

  var text = document.createElement('input');
  text.id = 'name';
  text.required = true;
  text.placeholder = 'Device name';

  var button = document.createElement('button');
  button.type = 'submit';
  button.textContent = 'Add';

  form.appendChild(text);
  form.appendChild(button);
  return form;
}

function updateRegistrations() {
  getRegistrations().then(function(registrations) {
    document.querySelector('#registrations').innerHTML = '';
    registrations.forEach(function(registration) {
      // TODO: include id to get unregistration really working.
      document.querySelector('#registrations').appendChild(
          createDeviceInfo(registration.name, registration.id));
    });
  });
}

// Update the current device status shown in the UI.
function updateStatus() {
  getCurrentRegistrationId().then(function(registration) {
    document.querySelector('#status').textContent = registration ? 'Registered' : 'Unregistered';
    document.querySelector('#current-registration').innerHTML = '';

    // Add registration field if not registered.
    if (!registration)
      document.querySelector('#current-registration').appendChild(createSubscriptionForm());
  });
}

function refreshUI() {
  updateStatus();
  updateRegistrations();
}

if (document.readyState == 'loading') {
  document.addEventListener('DOMContentLoaded', refreshUI);
}
