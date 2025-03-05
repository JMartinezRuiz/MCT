# MCT Dashboard

<div align="center">
  <img src="https://via.placeholder.com/150?text=MCT" alt="MCT Dashboard Logo" />
  <h3>Milestones, Checkpoints, and Tasks Dashboard</h3>
  <p>A lightweight project management system for individuals and small teams</p>
</div>

## 📋 Overview

MCT Dashboard is a Flask-based web application designed to help individuals and small teams manage projects effectively through a hierarchical structure:

- **Projects** → Top-level containers for your work
- **Milestones** → Major phases within projects
- **Checkpoints** → Specific deliverables or verification points
- **Tasks** → Individual work items to be completed

The system emphasizes simplicity and effectiveness for personal and small-scale projects, providing just enough structure without overwhelming complexity.

## ✨ Features

- **Hierarchical Project Structure**: Organize work from high-level projects down to individual tasks
- **Dependency Management**: Set conditions between tasks to manage workflow requirements
- **Problem Tracking**: Document and track issues at any level of your projects
- **Markdown Document Support**: Create and share project documentation with markdown formatting
- **Cost Tracking**: Monitor estimated costs at all levels of your projects
- **Team Collaboration**: Share notes and assign tasks to team members
- **Personal Notes**: Keep private notes for your own reference
- **Dashboard Analytics**: Get visual insights into project progress and status
- **Search Functionality**: Quickly find tasks and problems using codes or text search
- **Responsive Design**: Access your projects from desktop or mobile devices

## 🛠️ Technology Stack

- **Backend**: Python with Flask framework
- **Database**: SQLAlchemy ORM (supports SQLite by default, configurable for other databases)
- **Frontend**: Bootstrap 5, Chart.js for visualizations, FontAwesome for icons
- **Authentication**: Flask-Login for user management

## 🚀 Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/mct-dashboard.git
cd mct-dashboard
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Initialize the database**

```bash
flask init-db
```

5. **Run the development server**

```bash
python run.py
```

The application will be available at http://localhost:5000. Default login credentials are:
- Username: `admin`
- Password: `admin`

## 📦 Project Structure

```
mct-dashboard/
├── app/                    # Application package
│   ├── blueprints/         # View functions organized by feature
│   ├── forms/              # Form definitions
│   ├── models/             # Database models
│   ├── static/             # Static assets (CSS, JS, images)
│   ├── templates/          # HTML templates
│   ├── utils/              # Utility functions
│   ├── __init__.py         # Application factory
│   ├── config.py           # Configuration settings
│   └── extensions.py       # Flask extensions
├── uploads/                # Uploaded files
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md               # This file
```

## 🔄 Workflow

The basic workflow in MCT Dashboard follows this hierarchy:

1. Create a **Project** with basic information
2. Add **Milestones** to define major phases
3. Define **Checkpoints** within each milestone
4. Create **Tasks** that make up each checkpoint
5. Track **Problems** at any level when issues arise

Progress and completion are automatically calculated upwards through the hierarchy as tasks are completed.

## ⚙️ Configuration

Configuration options are defined in `app/config.py`. The most common settings to change are:

- `SECRET_KEY`: Set a secure random string in production
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: Location for document uploads
- `MAX_CONTENT_LENGTH`: Maximum upload size

For production deployment, create a `ProductionConfig` with secure settings.

## 📈 Development Roadmap

- [ ] Email notifications for task assignments and updates
- [ ] Calendar integration for timeline visualization
- [ ] File attachment support for tasks and problems
- [ ] API endpoints for integration with other tools
- [ ] Custom dashboard widgets
- [ ] Advanced reporting and export options

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

Project Link: [https://github.com/yourusername/mct-dashboard](https://github.com/yourusername/mct-dashboard)

---

<div align="center">
  <p>Built with ❤️ for better project management</p>
</div>
