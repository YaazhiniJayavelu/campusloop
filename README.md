# CampusLoop

A web app for college students that combines **Lost & Found** and **Skill Exchange** in one platform.

## Features

**Lost & Found**
- Post lost or found items with a photo, category and location
- Search and filter by keyword, category and status
- Suggested matches based on category, keywords and photo similarity (`imagehash`)
- Claim flow: the owner sends a claim and the finder approves or rejects it

**Skill Exchange**
- Coming soon

## Tech Stack

Python Flask, SQLite, Bootstrap, Flask-Login, Pillow, imagehash

## Installation

**Requirements:** Python 3.10 or newer, and Git.

1. Clone the repository:
```bash
   git clone https://github.com/YaazhiniJayavelu/campusloop.git
   cd campusloop
```

2. Create a virtual environment:
```bash
   python -m venv venv
```

3. Activate it:
```bash
   # Windows
   venv\Scripts\activate

   # Mac/Linux
   source venv/bin/activate
```

4. Install the dependencies:
```bash
   pip install -r requirements.txt
```

5. Run the app:
```bash
   python run.py
```

6. Open **http://127.0.0.1:5000** in your browser.

The SQLite database (`campusloop.db`) is created automatically on the first run.

## Usage

1. Register an account and log in
2. Click **Post Item** to report something lost or found
3. Open **Lost & Found** to search and filter items
4. Open your own item to see possible matches
5. Open someone else's item to send a claim

## Project Structure

```
campusloop/
├── app/
│   ├── auth/          # register, login, profile
│   ├── lostfound/     # items, claims, matching
│   ├── templates/
│   ├── static/uploads/
│   ├── models.py
│   └── __init__.py
├── config.py
├── run.py
└── requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file.