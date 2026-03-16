import subprocess
import sys

print("=" * 60)
print("Testing FastAPI Application")
print("=" * 60)

# Test import
print("\n1. Testing import...")
try:
    from rag_project.main import app
    print("   [OK] App imported successfully")
except Exception as e:
    print(f"   [FAILED] {e}")
    sys.exit(1)

# Check routes
print("\n2. Checking registered routes...")
api_routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        path = route.path
        if '/api/' in path or path == '/' or path == '/health':
            methods = list(route.methods)
            api_routes.append((path, methods))

print("   API Routes found:")
for path, methods in sorted(api_routes):
    print(f"     - {list(methods)[0]} {path}")

# Count expected routes
expected_paths = ['/', '/health',
                  '/api/auth/register', '/api/auth/login', '/api/auth/me', '/api/auth/api-key',
                  '/api/chat/sessions', '/api/chat/sessions/{session_id}/messages']

found_expected = []
missing_expected = []
for expected in expected_paths:
    found = any(expected.replace('{session_id}', '').strip('/') in path for path, _ in api_routes)
    if found:
        found_expected.append(expected)
    else:
        missing_expected.append(expected)

print(f"\n3. Expected routes check:")
print(f"   Found: {len(found_expected)}/{len(expected_paths)}")
if missing_expected:
    print(f"   Missing: {missing_expected}")

print("\n" + "=" * 60)
print("Test complete!")
