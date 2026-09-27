"""Local-mode entry point: run the event processor as a long-lived worker.

Invoked as ``python -m services.event_processor`` from Docker Compose. This
avoids re-importing ``handler`` as a top-level module (which would otherwise
trigger a runpy double-import warning) because the package is executed directly
as ``__main__`` and the reusable worker loop lives in ``handler.main``.
"""

from services.event_processor.handler import main

if __name__ == "__main__":
    main()
