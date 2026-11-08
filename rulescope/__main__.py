"""Entry point for `python3 -m rulescope` and also `python3 rulescope` (running the folder directly)."""
if __package__ in (None, ""):
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rulescope.cli import main
else:
    from .cli import main

raise SystemExit(main())
