#!/usr/bin/env python3
"""
Clean startup script for the Streamlit app
"""

import subprocess
import time
import os
import sys
import requests

def kill_all_processes():
    """Kill all Python and Streamlit processes"""
    print("🔪 Killing all processes...")
    subprocess.run(["pkill", "-9", "-f", "streamlit"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "python"], capture_output=True)
    time.sleep(3)

def clear_all_caches():
    """Clear all caches"""
    print("🧹 Clearing all caches...")
    subprocess.run(["find", ".", "-name", "*.pyc", "-delete"], capture_output=True)
    subprocess.run(["find", ".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"], capture_output=True)
    subprocess.run(["rm", "-rf", "~/.streamlit/"], capture_output=True)

def verify_simplified_implementation():
    """Verify the simplified implementation is in place"""
    print("🔍 Verifying simplified implementation...")
    try:
        with open("atlan_client.py", "r") as f:
            content = f.read()
            if "SIMPLIFIED IMPLEMENTATION" in content:
                print("✅ Simplified implementation found")
                return True
            else:
                print("❌ Simplified implementation NOT found")
                return False
    except Exception as e:
        print(f"❌ Error reading atlan_client.py: {e}")
        return False

def find_available_port():
    """Find an available port"""
    for port in range(8600, 8700):
        try:
            response = requests.get(f"http://localhost:{port}", timeout=1)
        except:
            return port
    return None

def start_app(port):
    """Start the app on a specific port"""
    print(f"🚀 Starting app on port {port}...")
    
    # Set environment variables
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-S_N3-OI2h814ONFCxnDw5w"
    env["ATLAN_API_TOKEN"] = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhUWEtTlRIRkkxU29BWHAtM1FDTzExcGhZY0w4dWNkeGVkMzBvN3ZuaHVnIn0.eyJleHAiOjE5MTE5NjEzNDIsImlhdCI6MTc1NDI4MTM0MiwianRpIjoiZjk2ZTUxODItMGFlNS00MGExLWI3YTMtNzViOWJhNGNjMTY2IiwiaXNzIjoiaHR0cHM6Ly9ob21lLmF0bGFuLmNvbS9hdXRoL3JlYWxtcy9kZWZhdWx0IiwiYXVkIjpbInJlYWxtLW1hbmFnZW1lbnQiLCJhY2NvdW50Il0sInN1YiI6IjIwMjQ1OGRmLTgwNGYtNGY4YS05MGQzLTYzZjk4YTFhYjg1NyIsInR5cCI6IkJlYXJlciIsImF6cCI6ImFwaWtleS0wZGJkMDdkNS05YjVlLTQ3ZGQtYTRjZC1hNDQ3OTJkZTA2ZDEiLCJyZXNvdXJjZV9hY2Nlc3MiOnsicmVhbG0tbWFuYWdlbWVudCI6eyJyb2xlcyI6WyJ2aWV3LXJlYWxtIiwidmlldy1pZGVudGl0eS1wcm92aWRlcnMiLCJtYW5hZ2UtaWRlbnRpdHktcHJvdmlkZXJzIiwiaW1wZXJzb25hdGlvbiIsInJlYWxtLWFkbWluIiwiY3JlYXRlLWNsaWVudCIsIm1hbmFnZS11c2VycyIsInF1ZXJ5LXJlYWxtcyIsInZpZXctYXV0aG9yaXphdGlvbiIsInF1ZXJ5LWNsaWVudHMiLCJxdWVyeS11c2VycyIsIm1hbmFnZS1ldmVudHMiLCJtYW5hZ2UtcmVhbG0iLCJ2aWV3LWV2ZW50cyIsInZpZXctdXNl"
    
    # Start the app with explicit Python path
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.headless", "true"
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for app to start
        time.sleep(15)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✅ App started on port {port}")
            return process
        else:
            print(f"❌ App failed to start on port {port}")
            stdout, stderr = process.communicate()
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return None

def test_app(port):
    """Test the app"""
    print(f"🧪 Testing app on port {port}...")
    
    try:
        response = requests.get(f"http://localhost:{port}", timeout=10)
        if response.status_code == 200:
            print("✅ App is responding")
            return True
        else:
            print(f"❌ App returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing app: {e}")
        return False

def main():
    print("🚀 Starting clean app startup...")
    
    # Step 1: Kill all processes
    kill_all_processes()
    
    # Step 2: Clear all caches
    clear_all_caches()
    
    # Step 3: Verify simplified implementation
    if not verify_simplified_implementation():
        print("❌ Simplified implementation not found. Cannot proceed.")
        return False
    
    # Step 4: Find available port
    port = find_available_port()
    if not port:
        print("❌ No available ports found")
        return False
    
    print(f"📍 Using port {port}")
    
    # Step 5: Start app
    process = start_app(port)
    if not process:
        return False
    
    # Step 6: Test app
    if test_app(port):
        print(f"✅ SUCCESS! App is working on port {port}")
        print(f"🌐 Open your browser to: http://localhost:{port}")
        print("🔍 Ask: 'Which assets use customer acquisition cost'")
        print("📝 Expected: 3 assets (Customer acquisition cost simple, Readme, Marketing Analytics)")
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping app...")
            process.terminate()
        
        return True
    else:
        print("❌ App test failed")
        if process:
            process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 