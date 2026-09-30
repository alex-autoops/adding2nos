"""Course 10: Perform CRUD against a Mock API. Python standard library only."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def show(value):
    print(json.dumps(value, indent=2) if not isinstance(value, str) else value)

class API(BaseHTTPRequestHandler):
    resource=None
    def log_message(self,*args):
        pass
    def reply(self,code,data=None):
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        if data is not None:
            self.wfile.write(json.dumps(data).encode())
    def do_GET(self):
        if self.path!='/items/1': return self.reply(404,{'error':'not found'})
        self.reply(200,API.resource) if API.resource is not None else self.reply(404,{'error':'not found'})
    def change(self,method):
        expected='/items' if method=='POST' else '/items/1'
        if self.path!=expected: return self.reply(404,{'error':'not found'})
        if method=='POST' and API.resource is not None: return self.reply(409,{'error':'already exists'})
        if method!='POST' and API.resource is None: return self.reply(404,{'error':'not found'})
        try: data=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))))
        except (ValueError,TypeError): return self.reply(400,{'error':'invalid JSON'})
        if not isinstance(data,dict): return self.reply(400,{'error':'object required'})
        if method=='PATCH': API.resource.update(data)
        else: API.resource=data
        self.reply(201 if method=='POST' else 200,API.resource)
    def do_POST(self): self.change('POST')
    def do_PUT(self): self.change('PUT')
    def do_PATCH(self): self.change('PATCH')
    def do_DELETE(self):
        if self.path!='/items/1' or API.resource is None: return self.reply(404,{'error':'not found'})
        API.resource=None
        self.reply(204)

def api_call(method):
    bodies={'POST':{'name':'demo','status':'new','note':'temporary'},'PUT':{'name':'demo','status':'replaced'},'PATCH':{'status':'ready'}}
    body=bodies.get(method)
    url='http://127.0.0.1:8765'+('/items' if method=='POST' else '/items/1')
    req=Request(url,data=json.dumps(body).encode() if body else None,method=method,headers={'Content-Type':'application/json'})
    try:
        with urlopen(req,timeout=5) as res: code,text=res.status,res.read().decode()
    except HTTPError as exc: code,text=exc.code,exc.read().decode()
    show(f'{method} {url} -> {code} {text}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=['serve', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    action = parser.parse_args().action
    if action == "serve":
        print("Mock API at http://127.0.0.1:8765. Stop with Ctrl+C.", flush=True)
        try:
            HTTPServer(("127.0.0.1", 8765), API).serve_forever()
        except KeyboardInterrupt:
            pass
    else:
        api_call(action)
