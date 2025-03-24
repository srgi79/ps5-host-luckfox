import os
import hashlib
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=host_dir, **kwargs)

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
    server_address = ('0.0.0.0', 80)
    httpd = TCPServer(server_address, RequestHandler)
    print(f"Starting host at {server_address[0]}:{server_address[1]}", flush=True)
    httpd.serve_forever()
