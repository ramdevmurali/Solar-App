from app import create_app

# Create the Flask app instance using the factory
app = create_app()

if __name__ == '__main__':
    # Run the app
    # debug=True will auto-reload the server when you make code changes
    # host='0.0.0.0' makes the server accessible from other devices on your network
    app.run(host='0.0.0.0', port=5001, debug=True)