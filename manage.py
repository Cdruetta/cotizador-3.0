#!/usr/bin/env python
"""Wrapper para ejecutar Django desde la raiz del repo."""

from pathlib import Path
import os
import runpy
import sys


if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent / "backend"
    os.chdir(backend_dir)
    sys.path.insert(0, str(backend_dir))
    # Inyectar --fake-initial en migrate para evitar DuplicateTable
    # cuando las tablas ya existen (migración desde esquema legacy).
    if len(sys.argv) > 1 and sys.argv[1] == "migrate" and "--fake-initial" not in sys.argv:
        sys.argv.append("--fake-initial")
    runpy.run_path(str(backend_dir / "manage.py"), run_name="__main__")

