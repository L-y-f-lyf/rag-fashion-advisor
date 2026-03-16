
#!/usr/bin/env python3
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python version:", sys.version)
print("Working directory:", os.getcwd())
print("Path:", sys.path)
print()

try:
    from rag_project.main import app
    print(f"✓ SUCCESS: App imported successfully - {type(app)}")

    # Check routes
    print("\nRegistered routes:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            print(f"  {route.methods} {route.path}")
except ImportError as e:
    print(f"✗ ImportError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
