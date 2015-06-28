// Requires helpers.js to be loaded.

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
    return fetch('/unregister',
                 { mode: 'same-origin', method: 'post', credentials: 'include',
                   body: JSON.stringify({ id: id }) }).then(function(response) {
      if (response.status != '200')
        return;
      getPushSubscription().then(function(subscription) {
        subscription.unsubscribe();
      });
    });
  };
  container.appendChild(button);

  return container;
}

function updateRegistrations() {
  getRegistrations().then(function(result) {
    registrations = result;

    registrations.forEach(function(registration) {
      // TODO: include id to get unregistration really working.
      document.querySelector('#registrations').appendChild(
          createDeviceInfo(registration.name, registration.id));
    });

    // TODO: be smarter and don't show "Add" if the device registration is in
    // the list.
    insertRegisterButton();
  });
}

// Update the current device status shown in the UI.
function updateStatus() {
  getCurrentRegistrationId().then(function(subscription) {
    document.querySelector('#status').textContent = subscription ? 'Registered' : 'Unregistered';
  });
}

if (document.readyState == 'loading') {
  document.addEventListener('DOMContentLoaded', function(e) {
    updateStatus();
    updateRegistrations();
  });
}
