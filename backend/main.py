from app import create_app
import os

# Create the Flask app instance using the factory
app = create_app()

if __name__ == '__main__':
    # Use the PORT environment variable if set (Render requirement), else default to 10000
    port = int(os.environ.get('PORT', 10000))
    # Run the app
    # debug=True will auto-reload the server when you make code changes
    # host='0.0.0.0' makes the server accessible from other devices on your network
    app.run(host='0.0.0.0', port=port, debug=True)