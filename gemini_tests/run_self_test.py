import os
import sys
import subprocess
import time

def install_dependencies():
    """Install required packages if not already installed."""
    print("Checking dependencies...")
    try:
        import playwright
        import pytest
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "gemini_tests/requirements.txt"])
        print("Installing Playwright browsers...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])

def run_tests():
    """Run the self-tests using pytest with Playwright."""
    print("\n=== Starting Self-Tests ===")
    print("Tests will run in a visible browser window (headed mode).")
    print("Target URL: http://localhost:5001")
    
    # Check if server is likely running (basic check)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5001))
    if result != 0:
        print("\n[WARNING] Port 5001 does not seem to be open.")
        print("Please make sure the Flask application is running in another terminal:")
        print("  python snowball.py")
        response = input("\nDo you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    # Run pytest
    # -s: Show stdout
    # --headed: Run with visible browser
    # --slowmo 1000: Slow down operations by 1000ms so user can see what's happening
    cmd = [
        sys.executable, "-m", "pytest", 
        "gemini_tests/test_scenarios.py", 
        "-s", 
        "--headed", 
        "--slowmo", "1000",
        "--video", "on"
    ]
    
    print(f"\nRunning command: {' '.join(cmd)}")
    subprocess.call(cmd)

if __name__ == "__main__":
    # Ensure we are in the project root
    if not os.path.exists("gemini_tests"):
        print("Error: Please run this script from the project root directory (e.g., c:\\Pythons\\snowball)")
        sys.exit(1)
        
    install_dependencies()
    run_tests()
