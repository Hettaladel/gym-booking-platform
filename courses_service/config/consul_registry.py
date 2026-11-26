import requests
import socket
import os

def register_with_consul():
    CONSUL_HOST = os.environ.get("CONSUL_HOST", "consul")
    CONSUL_PORT = os.environ.get("CONSUL_PORT", "8500")
    
    SERVICE_NAME = "courses-service"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8002))
    SERVICE_ADDRESS = os.environ.get("SERVICE_ADDRESS", "courses-service")
    
    consul_url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
    
    payload = {
        "Name": SERVICE_NAME,
        "ID": f"{SERVICE_NAME}-{socket.gethostname()}",
        "Address": SERVICE_ADDRESS,
        "Port": SERVICE_PORT,
        "Tags": [
            "traefik.enable=true",
            "traefik.http.routers.courses.rule=PathPrefix(`/api/courses`) || PathPrefix(`/api/sessions`)"
        ],
        # No check for now
    }
    
    try:
        response = requests.put(consul_url, json=payload, timeout=2)
        if response.status_code == 200:
            print(f"Successfully registered {SERVICE_NAME} with Consul")
        else:
            print(f"Failed to register with Consul: {response.text}")
    except Exception as e:
        print(f"Error connecting to Consul: {e}")
