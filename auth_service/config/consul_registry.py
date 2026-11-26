import requests
import socket
import os

def register_with_consul():
    # Only register if running in Docker/production (simple check)
    # or just try/except
    
    CONSUL_HOST = os.environ.get("CONSUL_HOST", "consul")
    CONSUL_PORT = os.environ.get("CONSUL_PORT", "8500")
    
    SERVICE_NAME = "auth-service"
    SERVICE_PORT = int(os.environ.get("SERVICE_PORT", 8001))
    # In Docker, hostname is container ID or service name if set.
    # We can use the service name from docker-compose as address if on same network
    SERVICE_ADDRESS = os.environ.get("SERVICE_ADDRESS", "auth-service")
    
    consul_url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/agent/service/register"
    
    payload = {
        "Name": SERVICE_NAME,
        "ID": f"{SERVICE_NAME}-{socket.gethostname()}",
        "Address": SERVICE_ADDRESS,
        "Port": SERVICE_PORT,
        "Tags": [
            "traefik.enable=true",
            "traefik.http.routers.auth.rule=PathPrefix(`/api/auth`) || PathPrefix(`/api/token`) || PathPrefix(`/api/users`)"
        ],
        "Check": {
            "HTTP": f"http://{SERVICE_ADDRESS}:{SERVICE_PORT}/api/users/me/",
            "Interval": "10s",
            "Timeout": "2s" # Note: requires authentication, check might fail 401. 
                            # Better check a public health endpoint.
        }
    }
    
    # Let's verify if we have a health check endpoint.
    # auth_service doesn't seem to have a dedicated health endpoint. 
    # 401 is considered failing by Consul? Default is "any 2xx code".
    # So we should probably remove the Check for now or add a health view.
    
    # Removing check for simplicity in this step, or pointing to admin login page?
    # Let's remove Check for now to avoid complexity, or add a simple health view.
    del payload["Check"]

    try:
        response = requests.put(consul_url, json=payload, timeout=2)
        if response.status_code == 200:
            print(f"Successfully registered {SERVICE_NAME} with Consul")
        else:
            print(f"Failed to register with Consul: {response.text}")
    except Exception as e:
        print(f"Error connecting to Consul: {e}")
