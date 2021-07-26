#!/usr/bin/env python
import configparser
import json
import socketserver

from pip._vendor import urllib3, certifi

try:
    import http.server as server
except ImportError:
    # Handle Python 2.x
    import SimpleHTTPServer as server

# Quite simply just grabbing docker host's container status to report it as a simple Home Assistance status.

global hostip
hostip = '192.168.1.1'
global hostport
hostport = 8000
class HTTPRequestHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        paths = self.path.split('/')
        http = urllib3.PoolManager(ca_certs=certifi.where())
        print(f'paths={paths}')
        stateresponse='{}'
        if 'status' in paths:
            container = paths[2]
            req = http.request("GET", f'http://{hostip}:{hostport}/v1.41/containers/{container}/json', redirect=False)
            if (req.status == 200):
                self.send_response(200, 'Coolio!')
                response = req.data.decode('utf-8')
                dockerdict = json.loads(response)
                statedict = {}
                statedict['Running'] = dockerdict['State']['Running']
                stateresponse = json.dumps(statedict)
            else:
                self.send_response(404, 'Container not found')
        else:
            self.send_response(404, "No idea what you're asking for.")
            self.end_headers()
            self.wfile.write(b'Sorry...not sure what you want from me.')
        self.end_headers()
        self.wfile.write(bytes(stateresponse, 'utf-8'))


if __name__ == '__main__':
    #server.test(HandlerClass=HTTPRequestHandler)
    PORT=8002
    Handler = HTTPRequestHandler
    config = configparser.ConfigParser()
    config.read('docker-ha-web.config')
    hostip = config['default']['ip']
    hostport = config['default']['port']
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Servint at port", PORT)
        httpd.serve_forever()