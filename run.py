from app.routes import create_app
import os
import sys

app = create_app()

if __name__ == "__main__":
    # Enable debug mode and force logging to flush
    debug_mode = True  # Force debug mode for better logging
    print("Starting Flask in debug mode for better logging...", flush=True)
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
