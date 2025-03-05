"""
Application entry point.
Run this file to start the Flask development server.
"""
from app import create_app
from app.config import DevelopmentConfig

# Create the application instance using development configuration
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    app.run(debug=True)