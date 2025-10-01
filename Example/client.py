import requests
import time
import sys

class SolverClient:
    def __init__(self, server_url='http://localhost:4848'):
        self.api_url = server_url
    
    def solve_image(self, image_path):
        try:

            with open(image_path, 'rb') as f:
                response = requests.post(
                    f"{self.api_url}/api/submit",
                    files={'image': f}
                )
            
            if not response.ok:
                print(f"HTTP Error {response.status_code}")
                return None
                
            data = response.json()
            req_id = data['request_id']
            print(f"ID: {req_id}")
            print(f"Position in queue: {data['queue_position']}")
            
            while True:
                response = requests.get(f"{self.api_url}/api/check/{req_id}")
                data = response.json()
                
                if data['status'] != 'PENDING':
                    return data['status']
                
                print(f"\rWaiting... Position: {data['queue_position']}", end="")
                time.sleep(1)
                
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            print()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: client.py <path_image>")
        sys.exit(1)
    
    client = SolverClient()
    result = client.solve_image(sys.argv[1])
    print(f"Result: {result}")