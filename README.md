# CampusLoop — integrated feature upgrade

This upgrade adds four modules to the existing Flask app while retaining Lost & Found and Skill Exchange:

- **Study Hub:** searchable subject resources, uploads and downloads.
- **Campus Events & Clubs:** create events, register/cancel registration, create clubs and join/leave.
- **Student Marketplace:** searchable listings, optional photos, prices, seller contact by email, mark sold/available, and delete your own listings.
- **Feedback & Polls:** create polls with 2–10 options, one vote per student per poll, results, close your own poll, and submit categorized feedback (including anonymous submissions).

## Install in one update

1. **Back up your existing project folder and `campusloop.db` first.**
2. Extract this ZIP into your existing project directory, allowing the updated files to replace files with the same names. This ZIP intentionally does **not** include a database file, so your existing `campusloop.db` and student data remain in place.
3. Activate the same Python virtual environment you use for CampusLoop.
4. Install dependencies if needed:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app as usual:
   ```bash
   python run.py
   ```
6. Open `http://127.0.0.1:5000/`, sign in, and use **Campus Hub** in the navigation. Flask-SQLAlchemy's existing `db.create_all()` creates the new tables automatically when the app starts.

## Notes

- File uploads use the app's configured upload folder and existing 5 MB request limit. Study Hub accepts PDF, DOC/DOCX, PPT/PPTX and TXT. Marketplace photos accept PNG, JPG/JPEG, WEBP and GIF.
- The app stores event date/time as entered in the browser; this initial version does not implement timezone conversion or event reminders.
- Marketplace seller contact uses the seller's registered email through the visitor's email app; no in-app messaging is included.
- Feedback is stored in the database. Anonymous submissions do not retain a user ID, and therefore won't appear in the submitter's personal feedback history.
- This project currently has no CSRF protection or admin moderation workflow. Before public deployment, add CSRF protection, configure a strong `SECRET_KEY` via environment variables, add moderation/admin controls, and review upload/security settings.
- For privacy and safety, only upload course materials you have permission to share, and don't include private or sensitive information in public posts.

## Existing functionality

The existing Lost & Found and Skill Exchange blueprints, models, and templates are retained. New database tables are additive; no existing tables are intentionally modified.
