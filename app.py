"""Campus event booking website.

Classroom prototype only. Run locally with sample data; no authentication or real payments.
"""
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from string import Template
from urllib.parse import parse_qs, urlparse
import json
import secrets
import sqlite3

from app_version import APP_VERSION
from events_catalogue import EVENTS

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'instance' / 'bookings.sqlite3'
TEMPLATE_PATH = ROOT / 'templates' / 'index.html'
STYLE_PATH = ROOT / 'static' / 'style.css'


def connect_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('''CREATE TABLE IF NOT EXISTS bookings (
        reference TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        attendee TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )''')
    connection.commit()
    return connection


def get_events():
    with connect_db() as connection:
        counts = {row['event_id']: row['total'] for row in connection.execute(
            'SELECT event_id, COUNT(*) AS total FROM bookings GROUP BY event_id')}
    return [{**event, 'booked': counts.get(event['id'], 0),
             'remaining': max(0, event['capacity'] - counts.get(event['id'], 0))}
            for event in EVENTS]


def build_cards():
    output = []
    for event in get_events():
        places = event['remaining']
        button = ('<button type="submit">Reserve a place &rarr;</button>' if places
                  else '<button type="button" disabled>Fully booked</button>')
        output.append(f'''<article class="event-card">
          <div class="event-top"><span class="category">{escape(event['category'])}</span>
          <span class="places">{places} places left</span></div>
          <h3>{escape(event['title'])}</h3>
          <p class="description">{escape(event['description'])}</p>
          <p class="details">{escape(event['date'])} · {escape(event['time'])}<br>{escape(event['location'])}</p>
          <form action="/book" method="post">
          <input type="hidden" name="event_id" value="{escape(event['id'])}">
          <label for="name-{escape(event['id'])}">Name for booking</label>
          <input id="name-{escape(event['id'])}" name="attendee" placeholder="e.g. Alex Demo"
             minlength="2" maxlength="60" required {'' if places else 'disabled'}>
          {button}</form></article>''')
    return '\n'.join(output)


def home(message='', error=False):
    page = Template(TEMPLATE_PATH.read_text(encoding='utf-8'))
    alert = ''
    if message:
        css = 'alert error' if error else 'alert success'
        alert = f'<div class="{css}" role="status">{escape(message)}</div>'
    return page.safe_substitute(version=escape(APP_VERSION), count=len(EVENTS),
                                alert=alert, cards=build_cards()).encode('utf-8')


def reserve(event_id, attendee):
    event = next((event for event in EVENTS if event['id'] == event_id), None)
    attendee = attendee.strip()
    if not event:
        return 'That event was not found.', True
    if len(attendee) < 2 or len(attendee) > 60:
        return 'Please enter a name between 2 and 60 characters.', True
    with connect_db() as connection:
        connection.execute('BEGIN IMMEDIATE')
        current = connection.execute('SELECT COUNT(*) FROM bookings WHERE event_id=?',
                                     (event_id,)).fetchone()[0]
        if current >= event['capacity']:
            return 'No places remain for this event.', True
        reference = 'EVT-' + secrets.token_hex(3).upper()
        connection.execute('INSERT INTO bookings(reference, event_id, attendee) VALUES(?, ?, ?)',
                           (reference, event_id, attendee))
        connection.commit()
    return f'Booked: {event["title"]}. Your reference is {reference}.', False


class EventsHandler(BaseHTTPRequestHandler):
    def respond(self, content, content_type='text/html; charset=utf-8', status=200):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            self.respond(home())
        elif path == '/health':
            self.respond(json.dumps({'status': 'ok', 'service': 'campus-events',
                                     'version': APP_VERSION}).encode(),
                         'application/json; charset=utf-8')
        elif path == '/api/events':
            self.respond(json.dumps(get_events()).encode(),
                         'application/json; charset=utf-8')
        elif path == '/static/style.css':
            self.respond(STYLE_PATH.read_bytes(), 'text/css; charset=utf-8')
        else:
            self.respond(b'<h1>404 - Page not found</h1>', status=404)

    def do_POST(self):
        if urlparse(self.path).path != '/book':
            self.respond(b'<h1>404 - Page not found</h1>', status=404)
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 1 or size > 2048:
                raise ValueError('Invalid form length')
            fields = parse_qs(self.rfile.read(size).decode('utf-8'))
            event_id = fields.get('event_id', [''])[0]
            attendee = fields.get('attendee', [''])[0]
            message, error = reserve(event_id, attendee)
        except (ValueError, UnicodeError):
            message, error = 'The booking form could not be read.', True
        self.respond(home(message, error), status=400 if error else 200)


if __name__ == '__main__':
    with connect_db():
        pass
    print('Campus Events running at http://127.0.0.1:5000')
    print('Use sample booking names; do not enter real student data.')
    ThreadingHTTPServer(('127.0.0.1', 5000), EventsHandler).serve_forever()
