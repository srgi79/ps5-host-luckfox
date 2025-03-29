
import os
import hashlib
import http.server, ssl, time, re #, cgi
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, HTTPServer

host_dir = 'document/en/ps5/'
payload_map_file = 'payload_map.js'

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        data = f.read()
        sha256_hash.update(data)
    return sha256_hash.hexdigest()

def generate_cache_manifest(directory_path, include_payloads=True):
    manifest = ["CACHE MANIFEST"]
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if '.appcache' in file:
                continue
            file_path = os.path.join(root, file)

            if not include_payloads and 'payload' in root:
                continue
            file_hash = calculate_file_hash(file_path)
            
            manifest_path = os.path.relpath(file_path, directory_path)
            if manifest_path.isspace() or manifest_path == '' or manifest_path == '.':
                manifest_path = '/'
                
            manifest_path = manifest_path.replace("\\","/")
            manifest.append(manifest_path + " #" + file_hash)

    return manifest

def generate_payload_map(directory_path, payload_map):
    found = False
    for root, _, files in os.walk(directory_path):
        for file in files:
            if payload_map in file:
                found = True
                break
            
        if found:
            # Create json
            lines = []
            lines.append("const payload_map =\n\t[\n")
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith(".bin") or file.endswith(".elf"):
                        obj = "\t\t{\n\
            displayTitle: '"+file+"', \n\
            description: '"+file+"', \n\
            fileName: '"+file+"', \n\
            author: '-', \n\
            source: '-', \n\
            version: '-', \n\
        },\n"
                        lines.append(obj)
            lines.append("\t];")
            with open(f"{directory_path}/{payload_map}", 'w+') as f:
                f.writelines(lines)
            print(f"Payload map generated in path: '{directory_path+payload_map}'", flush=True)
        else:
            print(f"{payload_map_file} not found in path: '{host_dir}'", flush=True)

class RequestHandler(SimpleHTTPRequestHandler):
    def replace_locale(self):
        self.path = re.sub('^\/document\/(\w{2})\/ps5', '/document/en/ps5/', self.path)
        #self.path = '/document/es/ps5/'

    def do_GET(self):
        self.replace_locale()
        return super().do_GET()

    def do_POST(self):
        self.replace_locale()
        tn = self.path.lstrip('document/en/ps5/')
        #print('!POST!: tn:\n'  + tn)
        fn = tn + '.bin' # '.json'
        if not tn.startswith("T_"):
            if fn!="a.bin":
                print('!POST!: INFO: '  + str(self.rfile.read(int(self.headers['Content-length']))),"utf-8", flush=True)
                return
            else:
                fn = time.strftime("%Y%m%d-%H%M%S") + ".json"

        print('!POST!: ' + self.path + ' -->> ' + fn, flush=True)
        print('test: %d'%int(self.headers['Content-length']), flush=True)
        data = self.rfile.read(int(self.headers['Content-length']))
        open("%s"%fn, "wb").write(data)

if __name__ == "__main__":

    # GENERATE CACHE
    cache_manifest = generate_cache_manifest(host_dir, True)

    output_path = "cache.appcache"
    output_path = os.path.join(host_dir, output_path)
    output_path = output_path.replace("\\","/")

    with open(output_path, "w+") as manifest_file:
        manifest_file.write("\n".join(cache_manifest))

    print(f"Cache manifest generated in path: '{output_path}'", flush=True)

    # GENERATE PAYLOAD MAP
    generate_payload_map(host_dir, payload_map_file)

    # HOST
    server_address = ('0.0.0.0', 443)
    httpd = HTTPServer(server_address, RequestHandler) #http.server.SimpleHTTPRequestHandler)
    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sslctx.check_hostname = False # If set to True, only the hostname that matches the certificate will be accepted
    sslctx.load_cert_chain(certfile='localhost.pem')
    httpd.socket = sslctx.wrap_socket(httpd.socket, server_side=True)
    print(f"Starting host at {server_address[0]}:{server_address[1]}", flush=True)
    httpd.serve_forever()
