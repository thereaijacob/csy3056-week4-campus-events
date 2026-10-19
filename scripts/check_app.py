"""Check application configuration and required files."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_version import APP_VERSION
from events_catalogue import EVENTS
from app import get_events, TEMPLATE_PATH, STYLE_PATH

assert isinstance(APP_VERSION, str) and APP_VERSION.count('.') == 2
assert len(EVENTS) >= 3
assert len(set(event['id'] for event in EVENTS)) == len(EVENTS)
assert all(event['capacity'] > 0 for event in EVENTS)
assert TEMPLATE_PATH.is_file() and STYLE_PATH.is_file()
assert all(event['remaining'] >= 0 for event in get_events())
print(f'Application check OK | Campus Events v{APP_VERSION} | {len(EVENTS)} events')
