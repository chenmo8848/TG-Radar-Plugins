from __future__ import annotations

import importlib
import pkgutil


def register_admin_plugins(registry) -> None:
    pkg_name = __name__
    for mod in pkgutil.iter_modules(__path__):
        if mod.name.startswith('_'):
            continue
        module = importlib.import_module(f'{pkg_name}.{mod.name}')
        register = getattr(module, 'register', None)
        if callable(register):
            register(registry)
