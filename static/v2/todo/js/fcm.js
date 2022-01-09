let firebaseConfig = {
  apiKey: "AIzaSyB7n1JJxN5dDjHUIJlDPRASYtQyPqrh_M4",
  authDomain: "rusel-by.firebaseapp.com",
  databaseURL: "https://rusel-by.firebaseio.com",
  projectId: "rusel-by",
  storageBucket: "rusel-by.appspot.com",
  messagingSenderId: "885812742855",
  appId: "1:885812742855:web:64d3566e039a677ee38ce2",
  measurementId: "G-51LD3ERLYQ"
};

firebase.initializeApp(firebaseConfig);
firebase.analytics();
const messaging = firebase.messaging();
messaging.usePublicVapidKey('BJFpDMgcjIFRzlDPFso1vdm_UhXnB7ddmV5S_vajNPINSxQxd440cU5TZwZW1njrsV_IxF3-ojfIjq5VptTNziw');

function isTokenSentToServer() {
  return window.localStorage.getItem('sentToServer') === '1';
}

function setTokenSentToServer(sent) {
  if (!sent)
    delTokenOnServer();
  window.localStorage.setItem('sentToServer', sent ? '1' : '0');
}

function tokenChanged(currentToken) {
  return (window.localStorage.getItem('firebaseToken') !== currentToken);
}

function sendTokenToServer(currentToken) {
  if (!isTokenSentToServer() || tokenChanged(currentToken)) {
    console.log('Sending token to server...');
    const url = 'https://rusel.by/todo/fcm_add/?token=' + currentToken;
    fetch(url)
      .then(function(response) { 
        return response.text().then(function(text) {
          console.log('Request succeeded with response "' + text + '"');
          if (text === 'true') {
            setTokenSentToServer(true);
            window.localStorage.setItem('firebaseToken', currentToken);
            }
          }); 
        })
      .catch(function (error) { console.log('Request failed', error); });
  } else {
    console.log('Token already sent to server so won\'t send it again unless it changes');
  }
}

function delTokenOnServer() {
  if (isTokenSentToServer()) {
    oldToken = window.localStorage.getItem('firebaseToken');
    if (oldToken) {
      console.log('Deleting a token on the server...');
      const url = 'https://rusel.by/todo/fcm_del/?token=' + oldToken;
      fetch(url)
        .then(function(response) { 
          return response.text().then(function(text) {
            console.log('Request succeeded with response "' + text + '"');
            if (text === 'true')
              window.localStorage.removeItem('firebaseToken');
            }); 
          })
        .catch(function (error) { console.log('Request failed', error); });
    }
  }
}

function showToken(currentToken) {
  const tokenElement = document.querySelector('#this_app_token');
  if (tokenElement)
    tokenElement.textContent = currentToken;
}

function resetUI() {
  showToken('loading...');
  messaging.getToken().then((currentToken) => {
    if (currentToken) {
      sendTokenToServer(currentToken);
      showToken(currentToken);
    } else {
      console.log('No Instance ID token available. Request permission to generate one.');
      showToken('No Instance ID token available.');
      setTokenSentToServer(false);
    }
  }).catch((err) => {
    console.log('An error occurred while retrieving token. ', err);
    showToken('Error retrieving Instance ID token. ', err);
    setTokenSentToServer(false);
  });
}

messaging.onTokenRefresh(() => {
  messaging.getToken().then((refreshedToken) => {
    console.log('Token refreshed.');
    setTokenSentToServer(false);
    sendTokenToServer(refreshedToken);
    resetUI();
  }).catch((err) => {
    console.log('Unable to retrieve refreshed token ', err);
    showToken('Unable to retrieve refreshed token ', err);
  });
});

navigator.serviceWorker.register('https://rusel.by/firebase-messaging-sw.js');

messaging.onMessage((payload) => {
  console.log('Message received. ', payload);
  navigator.serviceWorker.ready.then(function(registration) {
    registration.showNotification(payload.notification.title, payload.notification);
  });
});

// uncallable?
function requestPermission() {
  console.log('Requesting permission...');
  Notification.requestPermission().then((permission) => {
    if (permission === 'granted') {
      console.log('Notification permission granted.');
      resetUI();
    } else {
      console.log('Unable to get permission to notify.');
    }
  });
}

// uncallable?
function deleteToken() {
  messaging.getToken().then((currentToken) => {
    messaging.deleteToken(currentToken).then(() => {
      console.log('Token deleted.');
      setTokenSentToServer(false);
      resetUI();
    }).catch((err) => {
      console.log('Unable to delete token. ', err);
    });
  }).catch((err) => {
    console.log('Error retrieving Instance ID token. ', err);
    showToken('Error retrieving Instance ID token. ', err);
  });
}

resetUI();

