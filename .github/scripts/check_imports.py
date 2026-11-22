import importlib
import pkgutil
import sys

import zora.modules as modules_pkg

failed = []
for _, name, _ in pkgutil.iter_modules(modules_pkg.__path__):
    try:
        importlib.import_module(f"zora.modules.{name}")
    except Exception as e:
        failed.append((name, e))

try:
    import zora.main  # noqa: F401
except Exception as e:
    failed.append(("main", e))

if failed:
    for name, e in failed:
        print(f"::error::Failed to import {name}: {type(e).__name__}: {e}")
    sys.exit(1)

print("All modules imported successfully.")
