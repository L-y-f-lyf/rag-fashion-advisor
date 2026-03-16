import sys
sys.path.insert(0, 'rag_project')

print("Starting test...")
try:
    from main import app
    print(f"SUCCESS: App imported successfully - {type(app)}")
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
