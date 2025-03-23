import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080

# Change to the frontend directory
os.chdir(os.path.join(os.path.dirname(__file__), 'frontend'))

# Create custom handler
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # First, get the base path using the default implementation
        base_path = super().translate_path(path)
        
        # Handle /static/ paths specially
        if '/static/' in path:
            # Extract the part after '/static/'
            static_path = path.split('/static/', 1)[1]
            # Split into directories (css, js, etc.)
            parts = static_path.split('/')
            if len(parts) > 0:
                # First part is the subdirectory (css, js, etc.)
                subdir = parts[0]
                # Rebuild the path using the actual directories
                if os.path.exists(os.path.join(os.getcwd(), subdir)):
                    return os.path.join(os.getcwd(), *parts)
        
        return base_path
    
    def log_message(self, format, *args):
        # Custom logging to show where files are being served from
        print(f"{args[0]} {args[1]} - {self.path}")

# Set up request handler
Handler = CustomHTTPRequestHandler
Handler.extensions_map.update({
    '.js': 'application/javascript',
    '.html': 'text/html',
    '.css': 'text/css',
})

# Create server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving frontend files at http://localhost:{PORT}")
    print("To access the admin interface, go to:")
    print(f"http://localhost:{PORT}/admin-login-page.html")
    print("Press Ctrl+C to stop the server")
    print(f"Current directory: {os.getcwd()}")
    
    # Open browser automatically
    webbrowser.open(f'http://localhost:{PORT}/index.html')
    
    # Serve until interrupted
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.") 