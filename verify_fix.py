import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing import...")
try:
    from rag_project.main import app
    print(f"SUCCESS! App imported: {app}")

    # Print routes
    print("\nRoutes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {list(route.methods)} {route.path}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
