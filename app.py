import sys
from pathlib import Path

# Add bg_portal to python path to resolve modular imports
sys.path.insert(0, str(Path(__file__).parent / 'bg_portal'))

from bg_portal.app import create_app, app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
