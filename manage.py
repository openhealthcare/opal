#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    here = os.path.dirname(__file__)
    sys.path.append(here)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opal.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
