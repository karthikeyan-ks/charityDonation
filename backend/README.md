# Charity Website Project

A modern web application for managing charitable donations and fundraising activities.

## Project Structure

```
charity/
├── frontend/          # React-based frontend
├── backend/           # Django backend
│   ├── charity_backend/  # Main project directory
│   ├── users/           # User management app
│   ├── campaigns/       # Campaign management app
│   ├── donations/       # Donation management app
│   ├── manage.py       # Django management script
│   └── requirements.txt # Python dependencies
└── README.md         # Project documentation
```

## Features

- User authentication and authorization
- Donation management
- Campaign creation and management
- Payment integration
- Admin dashboard
- Responsive design

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js (v14 or higher)
- npm or yarn
- PostgreSQL (for backend)

### Installation

1. Clone the repository

2. Set up the backend:
   ```bash
   # Create and activate virtual environment
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Run migrations
   python manage.py migrate

   # Create superuser
   python manage.py createsuperuser

   # Run development server
   python manage.py runserver
   ```

3. Set up environment variables:
   - Create `.env` file in the backend directory
   - Add necessary environment variables (see `.env.example`)

4. Start the frontend development server:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## API Documentation

The API documentation is available at `/api/docs/` when running the Django development server.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 