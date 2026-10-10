# CampusLoop — Your Campus, Connected

CampusLoop is a web-based campus community platform designed to bring students together in one place. It helps students share academic resources, discover campus events, exchange skills, buy and sell items, participate in polls, and report lost or found belongings.

Built with Flask, Python, and a relational database, CampusLoop provides a centralized space for students to collaborate, communicate, and stay connected with campus life.

## Features

### 1. Lost & Found
- Post information about lost and found belongings.
- Browse available listings to help reunite students with their items.
- Share relevant details to make identifying and recovering belongings easier.

### 2. Skill Exchange
- Connect with fellow students to learn and share skills.
- Explore skills offered by other students.
- Create skill-related posts and find opportunities for peer-to-peer learning.

### 3. Study Hub
- Search for academic resources by subject.
- Upload and download supported study materials.
- Share learning resources to support collaborative studying.

Supported file formats: PDF, DOC, DOCX, PPT, PPTX, and TXT.

### 4. Campus Events & Clubs
- Discover campus events and student activities.
- Create events and register or cancel registrations.
- Create clubs and join or leave existing clubs.
- Keep students connected with campus activities and communities.

### 5. Student Marketplace
- Browse and search student marketplace listings.
- Create listings with descriptions, prices, and optional photos.
- Contact sellers through their registered email address.
- Mark your own listings as sold or available.
- Delete your own listings.

Supported photo formats: PNG, JPG, JPEG, WEBP, and GIF.

### 6. Feedback & Polls
- Create polls with 2–10 answer options.
- Vote once per student on each poll.
- View poll results and close polls you created.
- Submit categorized feedback.
- Submit feedback anonymously when preferred.

Anonymous feedback is not linked to a user account and does not appear in the submitter's personal feedback history.

### 7. Student Accounts
CampusLoop integrates with its existing account system to support sign-in and account-based functionality. Certain actions, such as managing your own listings or polls, require the appropriate authenticated account.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** Flask-SQLAlchemy with the database configured by the application
- **Frontend:** HTML, CSS, Bootstrap, and Jinja templates
- **Development environment:** Python virtual environment
- **Version control:** Git and GitHub

## Project Structure

```text
campusloop/
├── app/
│   ├── campus/          # Campus Hub routes
│   ├── skill/           # Skill Exchange routes
│   ├── static/
│   │   ├── css/         # Stylesheets
│   │   └── uploads/     # Uploaded files
│   ├── templates/       # HTML/Jinja templates
│   ├── __init__.py      # Flask application setup
│   └── models.py        # Database models
├── run.py               # Application entry point
├── requirements.txt     # Python dependencies
└── README.md
```

The exact project structure may vary depending on your local setup.

## Getting Started

### Prerequisites
- Python 3.10 or a compatible version for the installed dependencies
- pip
- Git (optional, for cloning the repository)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/YaazhiniJayavelu/campusloop.git
cd campusloop
```

If you already have the project locally, open its directory instead.

**2. Create and activate a virtual environment**

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```powershell
pip install -r requirements.txt
```

**4. Configure the application**

Set a secure Flask secret key using an environment variable and configure any database or upload settings required by your existing application. Do not commit secret keys, passwords, or other credentials to GitHub.

**5. Start the application**

```powershell
python run.py
```

**6. Open CampusLoop**

Visit:

http://127.0.0.1:5000/

Register or sign in, then use the navigation menu to explore the available features.

## Database

CampusLoop uses Flask-SQLAlchemy to manage its database models. If the application calls `db.create_all()` during startup, missing tables can be created automatically. This does not replace a proper database migration strategy when existing models or schemas change.

Back up your database before making structural changes. The repository should not contain private student data or a personal database file.

## File Uploads

The application supports uploads for academic resources and marketplace photos. Upload limits and storage locations depend on the application's configuration.

Only upload materials you have permission to share. Avoid uploading sensitive personal information, confidential academic documents, or files containing private student data.

## Security & Privacy

Before deploying CampusLoop publicly:

- Enable CSRF protection for forms.
- Store a strong `SECRET_KEY` in environment variables.
- Validate uploaded file types and sizes, and use safe filenames.
- Protect uploaded files and prevent unauthorized access.
- Add moderation and administrative controls for user-generated content.
- Apply appropriate authorization checks to every create, update, and delete action.
- Review database backups, privacy practices, and error handling.
- Avoid exposing student email addresses or personal information unnecessarily.

The current project does not include a complete moderation workflow or CSRF protection. Review these limitations before public deployment.

## Future Improvements

Potential enhancements include:

- Notifications and event reminders.
- In-app messaging between students.
- Improved search and filtering.
- Administrative moderation tools.
- Enhanced accessibility and mobile responsiveness.
- Automated tests and database migrations.

## Contributing

Contributions and suggestions are welcome. When modifying CampusLoop, test your changes locally before committing them, and avoid committing virtual environments, credentials, database files containing personal information, or unnecessary ZIP archives.

## License

Add the appropriate license information here if you intend to distribute or publish the project under an open-source license.

---

**CampusLoop — Learn together. Share resources. Build your campus community.**
