import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

# Add backend directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ["PYTHONPATH"] = str(project_root)


def check_qdrant():
    """Check if Qdrant is running through docker-compose"""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--status", "running"],
            capture_output=True, 
            text=True
        )
        if "qdrant" not in result.stdout:
            print("Qdrant not running - start with 'docker-compose up -d qdrant'")
            sys.exit(1)
        print("Qdrant is already running")
    except Exception as e:
        print(f"Qdrant check failed: {e}")
        sys.exit(1)

def start_django_backend():
    """Start the Django backend server"""
    print("Starting Django backend server...")
    try:
        subprocess.run(
            [
                "bash", 
                "-c",
                """
                # Start service and wait for container to be created
                docker compose up -d 
                
                # Wait max 30 seconds for container to enter running state
                timeout 30 bash -c "while ! docker compose ps --status running | grep -q decoviz_common; do sleep 1; done"
                
                # Follow logs only if container is running
                # docker compose logs -f decoviz_common
                """
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Entrypoint script failed: {e}")
        sys.exit(1)

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting backend server...")
    return subprocess.Popen(["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"])


def start_frontends():
    """Start Streamlit frontends"""
    print("Starting Streamlit frontends...")
    user_matching = subprocess.Popen(["streamlit", "run", "api/frontend/user_matching.py", "--server.port", "8501"])
    image_recommendation = subprocess.Popen(
        ["streamlit", "run", "api/frontend/image_recommendation.py", "--server.port", "8502"]
    )
    product_search = subprocess.Popen(["streamlit", "run", "api/frontend/product_search.py", "--server.port", "8503"])
    return user_matching, image_recommendation, product_search


def main():
    # Start Django backend
    django_backend_process = start_django_backend()
    
    # Start backend 
    backend_process = start_backend()
    
    # Start frontends
    user_matching_process, image_recommendation_process, product_search_process = start_frontends()

    try:
        # Open the applications in the default browser
        time.sleep(3)  # Wait for servers to start
        webbrowser.open("http://localhost:8501")  # User Matching UI
        webbrowser.open("http://localhost:8502")  # Image Recommendation UI
        webbrowser.open("http://localhost:8503")  # Product Search UI

        print("\nApplications are running!")
        print("User Matching UI: http://localhost:8501")
        print("Image Recommendation UI: http://localhost:8502")
        print("Product Search UI: http://localhost:8503")
        print("\nPress Ctrl+C to stop all services...")

        # Keep the script running
        django_backend_process.wait()
        backend_process.wait()
        user_matching_process.wait()
        image_recommendation_process.wait()
        product_search_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...") 
        django_backend_process.terminate()
        backend_process.terminate()
        user_matching_process.terminate()
        image_recommendation_process.terminate()
        product_search_process.terminate()
        print("Services stopped")


if __name__ == "__main__":
    main()
