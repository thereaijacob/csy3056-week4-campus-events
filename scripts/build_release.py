"""Create a clean installable-source ZIP; never package local attendee data."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app_version import APP_VERSION

files = [ROOT / filename for filename in (
    'app.py', 'app_version.py', 'events_catalogue.py', 'requirements.txt', 'README.md',
    'templates/index.html', 'static/style.css',
)]
missing = [str(p.relative_to(ROOT)) for p in files if not p.is_file()]
if missing:
    raise SystemExit(f'Package failed. Missing files: {", ".join(missing)}')
output_dir = ROOT / 'dist'
output_dir.mkdir(exist_ok=True)
archive = output_dir / f'campus-events-{APP_VERSION}.zip'
with ZipFile(archive, 'w', ZIP_DEFLATED) as zip_file:
    for p in files:
        zip_file.write(p, f'campus-events/{p.relative_to(ROOT).as_posix()}')
print(f'Created release artefact: {archive.relative_to(ROOT)}')
