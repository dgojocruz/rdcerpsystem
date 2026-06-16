#!/usr/bin/env python3
"""
ERP System — Main entry point
Usage:
  python run.py                        # Default client
  python run.py --client rhodeco       # Specific client
  python run.py --client new_co --setup "New Company Inc."  # Create & run new client
  python run.py --list-clients         # List all clients
  python run.py --port 5001            # Custom port
"""
import argparse
import os
import sys
import webbrowser
import threading
import time

# Fix path BEFORE any local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_browser(port, delay=1.5):
    time.sleep(delay)
    webbrowser.open(f'http://127.0.0.1:{port}')

def main():
    parser = argparse.ArgumentParser(description='ERP System')
    parser.add_argument('--client', '-c', help='Client ID to load', default=None)
    parser.add_argument('--setup', '-s', help='Company name for new client setup', default=None)
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port number (default: 5000)')
    parser.add_argument('--list-clients', action='store_true', help='List all clients')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    from app.config import list_clients, create_client

    if args.list_clients:
        clients = list_clients()
        if not clients:
            print("No clients configured yet.")
            print("Create one with: python run.py --client my_client --setup 'My Company Inc.'")
        else:
            print(f"\n{'CLIENT ID':<20} {'COMPANY':<40}")
            print('-' * 60)
            for c in clients:
                import json
                cfg_path = os.path.join('clients', c, 'config.json')
                name = ''
                if os.path.exists(cfg_path):
                    with open(cfg_path) as f:
                        d = json.load(f)
                    name = d.get('company_name', '')
                print(f"{c:<20} {name:<40}")
        return

    if args.client and args.setup:
        print(f"Creating new client: {args.client} — {args.setup}")
        create_client(args.client, args.setup)
        print(f"Client created. Database will be initialized on first run.")

    from app import create_app
    app = create_app(client_id=args.client)

    if args.debug:
        app.config['DEBUG'] = True

    if not args.no_browser:
        t = threading.Thread(target=open_browser, args=(args.port,), daemon=True)
        t.start()

    client_info = f" [{args.client}]" if args.client else ""
    print(f"\n{'='*55}")
    print(f"  ERP System{client_info} — Starting on port {args.port}")
    print(f"  URL: http://127.0.0.1:{args.port}")
    print(f"  Default login: admin / admin123")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*55}\n")

    app.run(host='127.0.0.1', port=args.port, debug=args.debug, use_reloader=False)

if __name__ == '__main__':
    main()
