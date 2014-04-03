#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analytics.settings")
    from django.core.management import execute_from_command_line
    extra_paths = ["."]
    for extra_path in extra_paths:
        if extra_path not in sys.path:
            sys.path.append(extra_path)

    execute_from_command_line(sys.argv)
