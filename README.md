# Timetable Scheduling System

The **Timetable Scheduling System** is a web-based application designed to help educational institutions efficiently manage and schedule timetables for faculties, students, and classrooms. It provides features for conflict resolution, timetable visualization, and user management.

## Features

- **Faculty Dashboard**: Allows faculty members to manage their schedules, add new courses, and resolve scheduling conflicts.
- **Student Timetable View**: Enables students to view their class schedules based on their division.
- **Conflict Detection and Resolution**: Automatically detects scheduling conflicts and provides alternative time slots for resolution.
- **Dynamic Timetable Generation**: Generates timetables dynamically for faculties and divisions.
- **User Authentication**: Secure login and registration for faculty members.

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Frontend**: HTML, CSS, JavaScript (with Jinja2 templating)
- **Authentication**: Flask-Login

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/JayDaftardar/timetables-scheduling.git
   cd timetables-scheduling
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open your browser and navigate to `http://127.0.0.1:5000`.

## Project Structure

```
ts/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── models.py              # Database models
├── utils.py               # Core scheduling logic
├── templates/             # HTML templates
│   ├── index.html         # Landing page
│   ├── faculty_dashboard.html
│   ├── student_dashboard.html
│   ├── add_schedule.html
│   ├── edit_schedule.html
│   ├── resolve_conflict.html
│   ├── resolve_edit_conflict.html
├── static/                # Static files (CSS, JS)
│   ├── style.css
│   ├── script.js
├── requirements.txt       # Python dependencies
├── .gitignore             # Git ignore file
```

## Usage

### Faculty
- **Login/Register**: Faculty members can log in or register via the landing page.
- **Manage Timetables**: Add, edit, or delete schedules from the dashboard.
- **Resolve Conflicts**: If a conflict arises, the system suggests alternative time slots.

### Students
- **View Timetables**: Students can view their division's timetable by selecting their division from the landing page.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push them to your fork.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or feedback, feel free to contact:
- **Author**: Jay Daftardar
- **Email**: jaydaftardar@gmail.com
