// Holds all open gever tabs
var clients = new Set();

onconnect = function(e) {
  var port = e.ports[0];
  clients.add(port);
  port.start();
  port.onmessage = function() {
    // Broadcast logout message to all open gever tabs
    clients.forEach(c => { c.postMessage('logout'); });
  };
};
