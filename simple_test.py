import subprocess
import sys

# First try: direct import test
print("TEST 1: Direct Import")
result = subprocess.run(
    [sys.executable, '-c', 'from rag_project.main import app; print("OK - imported successfully")'],
    capture_output=True,
    text=True,
    cwd='C:\\Users\\yafei\\PycharmProjects\\PythonProject1'
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
