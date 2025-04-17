# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from datetime import datetime

from config import Config
from models import db, Faculty, Division, Room, TimeSlot, Course
from utils import TimetableScheduler

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure database directory exists
os.makedirs('database', exist_ok=True)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Faculty.query.get(int(user_id))

# Create database tables
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Add some initial data if the database is empty
    if not TimeSlot.query.first():
        # Create time slots
        time_slots = [
            # Monday slots
            TimeSlot(day='Monday', start_time=datetime.strptime('09:00', '%H:%M').time(), 
                    end_time=datetime.strptime('10:00', '%H:%M').time()),
            TimeSlot(day='Monday', start_time=datetime.strptime('10:00', '%H:%M').time(), 
                    end_time=datetime.strptime('11:00', '%H:%M').time()),
            TimeSlot(day='Monday', start_time=datetime.strptime('11:00', '%H:%M').time(), 
                    end_time=datetime.strptime('12:00', '%H:%M').time()),
            TimeSlot(day='Monday', start_time=datetime.strptime('13:00', '%H:%M').time(), 
                    end_time=datetime.strptime('14:00', '%H:%M').time()),
            TimeSlot(day='Monday', start_time=datetime.strptime('14:00', '%H:%M').time(), 
                    end_time=datetime.strptime('15:00', '%H:%M').time()),
            # Tuesday slots
            TimeSlot(day='Tuesday', start_time=datetime.strptime('09:00', '%H:%M').time(), 
                    end_time=datetime.strptime('10:00', '%H:%M').time()),
            TimeSlot(day='Tuesday', start_time=datetime.strptime('10:00', '%H:%M').time(), 
                    end_time=datetime.strptime('11:00', '%H:%M').time()),
            TimeSlot(day='Tuesday', start_time=datetime.strptime('11:00', '%H:%M').time(), 
                    end_time=datetime.strptime('12:00', '%H:%M').time()),
            TimeSlot(day='Tuesday', start_time=datetime.strptime('13:00', '%H:%M').time(), 
                    end_time=datetime.strptime('14:00', '%H:%M').time()),
            TimeSlot(day='Tuesday', start_time=datetime.strptime('14:00', '%H:%M').time(), 
                    end_time=datetime.strptime('15:00', '%H:%M').time()),
            # Add more time slots for other days
            # Wednesday slots
            TimeSlot(day='Wednesday', start_time=datetime.strptime('09:00', '%H:%M').time(), 
                    end_time=datetime.strptime('10:00', '%H:%M').time()),
            TimeSlot(day='Wednesday', start_time=datetime.strptime('10:00', '%H:%M').time(), 
                    end_time=datetime.strptime('11:00', '%H:%M').time()),
            TimeSlot(day='Wednesday', start_time=datetime.strptime('11:00', '%H:%M').time(), 
                    end_time=datetime.strptime('12:00', '%H:%M').time()),
            TimeSlot(day='Wednesday', start_time=datetime.strptime('13:00', '%H:%M').time(), 
                    end_time=datetime.strptime('14:00', '%H:%M').time()),
            TimeSlot(day='Wednesday', start_time=datetime.strptime('14:00', '%H:%M').time(), 
                    end_time=datetime.strptime('15:00', '%H:%M').time()),
            # Thursday slots
            TimeSlot(day='Thursday', start_time=datetime.strptime('09:00', '%H:%M').time(), 
                    end_time=datetime.strptime('10:00', '%H:%M').time()),
            TimeSlot(day='Thursday', start_time=datetime.strptime('10:00', '%H:%M').time(), 
                    end_time=datetime.strptime('11:00', '%H:%M').time()),
            TimeSlot(day='Thursday', start_time=datetime.strptime('11:00', '%H:%M').time(), 
                    end_time=datetime.strptime('12:00', '%H:%M').time()),
            TimeSlot(day='Thursday', start_time=datetime.strptime('13:00', '%H:%M').time(), 
                    end_time=datetime.strptime('14:00', '%H:%M').time()),
            TimeSlot(day='Thursday', start_time=datetime.strptime('14:00', '%H:%M').time(), 
                    end_time=datetime.strptime('15:00', '%H:%M').time()),
            # Friday slots
            TimeSlot(day='Friday', start_time=datetime.strptime('09:00', '%H:%M').time(), 
                    end_time=datetime.strptime('10:00', '%H:%M').time()),
            TimeSlot(day='Friday', start_time=datetime.strptime('10:00', '%H:%M').time(), 
                    end_time=datetime.strptime('11:00', '%H:%M').time()),
            TimeSlot(day='Friday', start_time=datetime.strptime('11:00', '%H:%M').time(), 
                    end_time=datetime.strptime('12:00', '%H:%M').time()),
            TimeSlot(day='Friday', start_time=datetime.strptime('13:00', '%H:%M').time(), 
                    end_time=datetime.strptime('14:00', '%H:%M').time()),
            TimeSlot(day='Friday', start_time=datetime.strptime('14:00', '%H:%M').time(), 
                    end_time=datetime.strptime('15:00', '%H:%M').time()),
        ]
        
        for time_slot in time_slots:
            db.session.add(time_slot)
        
        # Create divisions
        divisions = [
            Division(name='Division A'),
            Division(name='Division B'),
            Division(name='Division C')
        ]
        
        for division in divisions:
            db.session.add(division)
        
        # Create rooms
        rooms = [
            Room(name='Room 101', capacity=30, is_lab=False),
            Room(name='Room 102', capacity=40, is_lab=False),
            Room(name='Room 103', capacity=35, is_lab=False),
            Room(name='Lab 201', capacity=25, is_lab=True),
            Room(name='Lab 202', capacity=30, is_lab=True)
        ]
        
        for room in rooms:
            db.session.add(room)
        
        # Commit changes
        db.session.commit()

# Routes
@app.route('/')
def index():
    divisions = Division.query.all()
    return render_template('index.html', divisions=divisions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        faculty = Faculty.query.filter_by(username=username).first()
        
        if faculty and faculty.check_password(password):
            login_user(faculty)
            flash('Login successful!', 'success')
            return redirect(url_for('faculty_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        department = request.form.get('department')
        
        # Check if username or email already exists
        existing_user = Faculty.query.filter((Faculty.username == username) | (Faculty.email == email)).first()
        
        if existing_user:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('register'))
        
        # Create new faculty account
        new_faculty = Faculty(username=username, email=email, name=name, department=department)
        new_faculty.set_password(password)
        
        db.session.add(new_faculty)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    # Get the timetable for the current faculty
    timetable = TimetableScheduler.get_timetable_for_faculty(current_user.id)
    return render_template('faculty_dashboard.html', timetable=timetable)

@app.route('/faculty/add_schedule', methods=['GET', 'POST'])
@login_required
def add_schedule():
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        division_id = request.form.get('division_id')
        room_id = request.form.get('room_id')
        time_slot_id = request.form.get('time_slot_id')
        
        # Try to schedule the course
        success, message, course, conflict_details = TimetableScheduler.schedule_course(
            current_user.id, 
            division_id, 
            room_id, 
            time_slot_id, 
            course_name
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('faculty_dashboard'))
        else:
            # Store the course information in the session for the resolve conflict page
            session['pending_course'] = {
                'name': course_name,
                'division_id': division_id,
                'room_id': room_id,
                'faculty_id': current_user.id,
                'original_time_slot_id': time_slot_id  # Add the original time slot ID
            }
            
            # Get available time slots for this faculty and room
            available_slots = TimetableScheduler.get_available_slots(current_user.id, room_id)
            
            # If no available slots, let the faculty know
            if not available_slots:
                flash("No available time slots for this room. Please try a different room.", "danger")
                return redirect(url_for('add_schedule'))
            
            # Return the resolve conflict template with all necessary data
            return render_template(
                'resolve_conflict.html', 
                available_slots=available_slots,
                conflict_details=conflict_details,
                course_name=course_name,
                division_id=division_id,
                room_id=room_id,
                room=Room.query.get(room_id),
                division=Division.query.get(division_id),
                requested_slot=TimeSlot.query.get(time_slot_id)
            )
    
    # Get all divisions, rooms, and time slots for the form
    divisions = Division.query.all()
    rooms = Room.query.all()
    time_slots = TimeSlot.query.order_by(TimeSlot.day, TimeSlot.start_time).all()  # Order time slots
    
    # Group time slots by day for easier selection
    grouped_time_slots = {}
    for slot in time_slots:
        if slot.day not in grouped_time_slots:
            grouped_time_slots[slot.day] = []
        grouped_time_slots[slot.day].append(slot)
    
    return render_template('add_schedule.html', 
                          divisions=divisions, 
                          rooms=rooms, 
                          time_slots=time_slots,
                          grouped_time_slots=grouped_time_slots)

@app.route('/faculty/resolve_conflict', methods=['POST'])
@login_required
def resolve_conflict():
    # Get data from the form
    course_name = request.form.get('course_name')
    division_id = request.form.get('division_id')
    room_id = request.form.get('room_id')
    time_slot_id = request.form.get('time_slot_id')
    
    if not all([course_name, division_id, room_id, time_slot_id]):
        flash("Missing required information. Please try again.", "danger")
        return redirect(url_for('add_schedule'))
    
    # Schedule the course with the selected alternative time slot
    success, message, course, conflict_details = TimetableScheduler.schedule_course(
        current_user.id, 
        division_id, 
        room_id, 
        time_slot_id, 
        course_name
    )
    
    if success:
        flash(message, 'success')
        # Clear the session data
        if 'pending_course' in session:
            session.pop('pending_course')
        return redirect(url_for('faculty_dashboard'))
    else:
        # If there's still a conflict, show available slots again
        available_slots = TimetableScheduler.get_available_slots(current_user.id, room_id)
        
        if not available_slots:
            flash("No available time slots for this room. Please try a different room.", "danger")
            return redirect(url_for('add_schedule'))
        
        return render_template(
            'resolve_conflict.html', 
            available_slots=available_slots,
            conflict_details=conflict_details,
            course_name=course_name,
            division_id=division_id,
            room_id=room_id,
            room=Room.query.get(room_id),
            division=Division.query.get(division_id),
            requested_slot=TimeSlot.query.get(time_slot_id)
        )

@app.route('/faculty/edit_schedule/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if the current faculty owns this course
    if course.faculty_id != current_user.id:
        flash('You are not authorized to edit this course.', 'danger')
        return redirect(url_for('faculty_dashboard'))
    
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        division_id = request.form.get('division_id')
        room_id = request.form.get('room_id')
        time_slot_id = request.form.get('time_slot_id')
        
        # Check if the new room/time is different from the current one
        is_changing_slot = (course.room_id != int(room_id) or course.time_slot_id != int(time_slot_id))
        
        # Only need to check availability if changing the time or room
        is_available = True
        if is_changing_slot:
            is_available = TimetableScheduler.check_availability(current_user.id, room_id, time_slot_id)
        
        if is_available or not is_changing_slot:
            # Update the course
            course.name = course_name
            course.division_id = division_id
            course.room_id = room_id
            course.time_slot_id = time_slot_id
            db.session.commit()
            
            # Update data structures
            TimetableScheduler._initialize_data_structures()
            
            flash('Course updated successfully.', 'success')
            return redirect(url_for('faculty_dashboard'))
        else:
            # Store the course information for the resolve conflict page
            session['pending_edit'] = {
                'course_id': course_id,
                'name': course_name,
                'division_id': division_id,
                'room_id': room_id,
            }
            
            # Get conflict details
            conflict_details = TimetableScheduler.get_conflict_details(current_user.id, room_id, time_slot_id)
            
            # Get available time slots for this faculty and room
            available_slots = TimetableScheduler.get_available_slots(current_user.id, room_id)
            
            # If no available slots, let the faculty know
            if not available_slots:
                flash("No available time slots for this room. Please try a different room.", "danger")
                return redirect(url_for('edit_schedule', course_id=course_id))
            
            return render_template(
                'resolve_edit_conflict.html', 
                available_slots=available_slots,
                conflict_details=conflict_details,
                course=course,
                course_name=course_name,
                division_id=division_id,
                room_id=room_id,
                room=Room.query.get(room_id),
                division=Division.query.get(division_id),
                requested_slot=TimeSlot.query.get(time_slot_id)
            )
    
    # Get all divisions, rooms, and time slots for the form
    divisions = Division.query.all()
    rooms = Room.query.all()
    time_slots = TimeSlot.query.all()
    
    return render_template('edit_schedule.html', course=course, divisions=divisions, rooms=rooms, time_slots=time_slots)

@app.route('/faculty/resolve_edit_conflict', methods=['POST'])
@login_required
def resolve_edit_conflict():
    # Get data from the form
    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name')
    division_id = request.form.get('division_id')
    room_id = request.form.get('room_id')
    time_slot_id = request.form.get('time_slot_id')
    
    course = Course.query.get_or_404(course_id)
    
    # Check if the current faculty owns this course
    if course.faculty_id != current_user.id:
        flash('You are not authorized to edit this course.', 'danger')
        return redirect(url_for('faculty_dashboard'))
    
    # Check availability with the new time slot
    is_available = TimetableScheduler.check_availability(current_user.id, room_id, time_slot_id)
    
    if is_available:
        # Update the course
        course.name = course_name
        course.division_id = division_id
        course.room_id = room_id
        course.time_slot_id = time_slot_id
        db.session.commit()
        
        # Update data structures
        TimetableScheduler._initialize_data_structures()
        
        flash('Course updated successfully.', 'success')
    else:
        flash('The selected time slot is also not available. Please try again.', 'danger')
    
    # Clear the session data
    if 'pending_edit' in session:
        session.pop('pending_edit')
    
    return redirect(url_for('faculty_dashboard'))

@app.route('/faculty/delete_schedule/<int:course_id>')
@login_required
def delete_schedule(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if the current faculty owns this course
    if course.faculty_id != current_user.id:
        flash('You are not authorized to delete this course.', 'danger')
        return redirect(url_for('faculty_dashboard'))
    
    db.session.delete(course)
    db.session.commit()
    
    # Update data structures
    TimetableScheduler._initialize_data_structures()
    
    flash('Course deleted successfully.', 'success')
    return redirect(url_for('faculty_dashboard'))

@app.route('/student/timetable/<int:division_id>')
def student_timetable(division_id):
    division = Division.query.get_or_404(division_id)
    timetable = TimetableScheduler.get_timetable_for_division(division_id)
    divisions = Division.query.all()
    
    return render_template('student_dashboard.html', timetable=timetable, division=division, divisions=divisions)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)