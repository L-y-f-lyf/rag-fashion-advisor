import sys
import subprocess
import time
import threading

def run_with_timeout(cmd, timeout=10):
    """Run command with timeout"""
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='C:\\Users\\yafei\\PycharmProjects\\PythonProject1'
    )

    def kill_process():
        time.sleep(timeout)
        if process.poll() is None:
            process.kill()

    # Start timeout thread
    timer = threading.Thread(target=kill_process)
    timer.daemon = True
    timer.start()

    try:
        stdout, stderr = process.communicate(timeout=timeout+1)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.stdout.read(), process.stderr.read()
        return -1, stdout, stderr

# Test import
print("=" * 60)
print("TESTING APP IMPORT")
print("=" * 60)
returncode, stdout, stderr = run_with_timeout('python -c "from rag_project.main import app; print(\"SUCCESS\")"')

print("\nSTDOUT:", stdout)
print("STDERR:", stderr)
print("RETURN CODE:", returncode)
