import requests
import socket
import os

def register_with_consul():
    CONSUL_HOST = os.environ.get("CONSUL_HOST", "consul")
    CONSUL_PORT = os.environ.get("CONSUL_PORT", "8500")
    
    SERVICE_NAME = "reservations-service"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8003))
    SERVICE_ADDRESS = os.environ.get("SERVICE_ADDRESS", "reservations-service")
    
    consul_url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
    
    payload = {
        "Name": SERVICE_NAME,
        "ID": f"{SERVICE_NAME}-{socket.gethostname()}",
        "Address": SERVICE_ADDRESS,
        "Port": SERVICE_PORT,
        "Tags": [
            "traefik.enable=true",
            "traefik.http.routers.reservations.rule=PathPrefix(`/api/reservations`)"
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

def discover_service(service_name):
    CONSUL_HOST = os.environ.get("CONSUL_HOST", "consul")
    CONSUL_PORT = os.environ.get("CONSUL_PORT", "8500")
    url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/catalog/service/{service_name}"
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            services = resp.json()
            if services:
                # Basic load balancing: pick first
                svc = services[0]
                addr = svc['ServiceAddress'] or svc['Address']
                port = svc['ServicePort']
                return f"http://{addr}:{port}"
    except:
        pass
    return None
