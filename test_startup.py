import sys
import os

sys.path.insert(0, '.')

print("=" * 60)
print("Testing app startup")
print("=" * 60)

# Import the app (without triggering startup)
from rag_project.main import app
print(f"\nApp imported successfully: {app}")

# Check routes before startup
print("\nRoutes BEFORE startup:")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")

# Manually trigger startup events
print("\nTriggering startup events...")
import asyncio
asyncio.run(app.event_handler("startup"))()

# Check routes after startup
print("\nRoutes AFTER startup (excluding docs):")
for route in app.routes:
    if hasattr(route, 'path') and not route.path.startswith('/openapi') and route.path != '/docs' and route.path != '/redoc':
        print(f"  {route.path}")

print("\n[Done]")
