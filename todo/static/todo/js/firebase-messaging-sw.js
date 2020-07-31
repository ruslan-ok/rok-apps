importScripts('https://www.gstatic.com/firebasejs/7.16.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.16.1/firebase-messaging.js');

var firebaseConfig = {
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
const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = 'Background Message Title';
  const notificationOptions = {
    body: 'Background Message body.',
    icon: '/static/todo/img/firebase-logo.png'
  };

  return self.registration.showNotification(notificationTitle,
    notificationOptions);
});

self.onnotificationclick = function(event) {
  console.log('On notification click: ', event.notification);
  console.log('action: ', event.action);

  const url = 'https://rusel.by/todo/' + event.action + '/' + event.notification.tag + '/';
  fetch(url)
    .then(function(response) { 
      return response.text().then(function(text) {
        console.log('Request succeeded with response:\n' + text);
        }); 
      })
    .catch(function (error) { console.log('Request failed', error); });
  
  event.notification.close();
};

