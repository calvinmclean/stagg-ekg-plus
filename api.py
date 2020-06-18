import http.server
from io import BytesIO
import socketserver
from stagg_ekg_plus import StaggEKG

PORT = 8000
MAC = "00:1C:97:18:7B:04"

class web_server(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print("GET REQUEST RECEIVED")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if self.path == "/state":
            print("Getting state")
            state = 1 if stagg.get_current_temp() > 32 else 0
            print("value =", str(state))
            self.wfile.write(bytes(str(state), "utf-8"))
        elif self.path == "/target_temp":
            print("Getting target temp")
            temp = stagg.get_target_temp()
            print("value =", str(temp))
            self.wfile.write(bytes(str(temp), "utf-8"))
        elif self.path == "/current_temp":
            print("Getting current temp")
            temp = stagg.get_current_temp()
            print("value =", str(temp))
            self.wfile.write(bytes(str(temp), "utf-8"))

    def do_POST(self):
        print("POST REQUEST RECEIVED")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode("utf-8")
        print(self.path)
        data = {body.split("=")[0]: body.split("=")[1]}
        print("Received request:", data)
        if self.path == "/state":
            if data['value'] == "0":
                print("Turning kettle OFF")
                stagg.off()
            else:
                print("Turning kettle ON")
                stagg.on()
        elif self.path == "/target_temp":
            degree_f = round(convert_c_to_f(float(data['value'])))
            print("Setting target temperature to:", degree_f)
            stagg.set_temp(degree_f)
            self.wfile.write(bytes(str(degree_f), "utf-8"))
        self.send_response(200)
        self.end_headers()

stagg = StaggEKG(MAC)

def convert_c_to_f(temp):
    "Converts Celsius to Fahrenheit."
    conversion = round(9.0 / 5.0 * temp + 32, 2)
    return conversion

with socketserver.TCPServer(("localhost", PORT), web_server) as httpd:
    # httpd.serve_forever()
    print("STARTED")
    try:
        httpd.serve_forever()
    except Exception:
        httpd.shutdown()
