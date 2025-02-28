# Operations Checklists

A Flask application for managing operations checklists.

## Features

- Create and manage checklist templates with customizable items
- Generate daily checklists based on templates
- Complete checklists with time and status (OK/Fail) for each item
- Send completed checklists via email to configured recipients
- Manage email recipients

## Installation

1. Clone the repository:

```
git clone <repository-url>
cd ops_checklists
```

2. Create and activate a virtual environment:

```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Initialize the database:

```
python init_db.py
```

## Configuration

Configure the application by setting environment variables or by creating a `.env` file in the project root:

```
# Flask configuration
SECRET_KEY=your-secret-key

# Email configuration (optional, for sending checklists)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@example.com
```

## Running the Application

Start the development server:

```
python run.py
```

The application will be available at http://localhost:5000

## Usage

1. **Templates**: Create checklist templates with groups and items
2. **Checklists**: Create daily checklists based on templates and complete them
3. **Admin**: Manage email recipients for sending completed checklists

## License

This project is licensed under the MIT License - see the LICENSE file for details.
