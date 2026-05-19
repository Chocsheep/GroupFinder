from app import app, socketio
import os

if __name__ == '__main__':
    # Railway injects its own port via environment variable  
    port = int(os.environ.get("PORT", 5000))

    # lets Railway's network reach the app
    app.run(debug=False, host="0.0.0.0", port=port)