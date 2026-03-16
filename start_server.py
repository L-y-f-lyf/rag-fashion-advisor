import subprocess
import time
import sys

# Start uvicorn in background
print("Starting uvicorn...")
process = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'rag_project.main:app', '--host', '0.0.0.0', '--port', '8000'],
    cwd='C:\\Users\\yafei\\PycharmProjects\\PythonProject1',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for startup
time.sleep(5)

# Check output
stdout, stderr = process.communicate(timeout=2)

print("STDOUT:")
print(stdout)
print("\nSTDERR:")
print(stderr)
print(f"\nReturn code: {process.returncode}")
