from app import create_app
from datetime import datetime

app = create_app()

# Add template global variables
@app.context_processor
def inject_globals():
    return {
        'now': datetime.now()
    }

if __name__ == '__main__':
    app.run(debug=True)
