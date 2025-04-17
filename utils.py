# utils.py
from models import db, Course, Faculty, Room, TimeSlot, Division

class Node:
    """Node class for linked list implementation."""
    def __init__(self, course=None, next_node=None):
        # Node object stores course data and reference to next node
        self.course = course
        self.next = next_node

class LinkedList:
    """Linked list implementation for course tracking."""
    def __init__(self):
        # Data Structure: Singly Linked List
        # Head pointer - entry point to the linked list
        self.head = None
    
    def add(self, course):
        """Add a course to the linked list."""
        # Data Structure Operation: Insertion at end - O(n) time complexity
        new_node = Node(course)
        if not self.head:
            self.head = new_node
            return
        
        # Traverse to end of list
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def find_by_faculty_and_time(self, faculty_id, time_slot_id):
        """Find a course by faculty ID and time slot ID."""
        # Data Structure Operation: Linear search - O(n) time complexity
        current = self.head
        while current:
            if current.course.faculty_id == faculty_id and current.course.time_slot_id == time_slot_id:
                return current.course
            current = current.next
        return None
    
    def find_by_room_and_time(self, room_id, time_slot_id):
        """Find a course by room ID and time slot ID."""
        current = self.head
        while current:
            if current.course.room_id == room_id and current.course.time_slot_id == time_slot_id:
                return current.course
            current = current.next
        return None

class TimetableScheduler:
    """Handles the core scheduling logic for the timetable system."""
    
    # Class-level data structures
    _courses_linked_list = LinkedList()
    _faculty_schedule = {}  # Hash table for faculty schedules
    _room_schedule = {}     # Hash table for room schedules
    _timetable_matrix = {}  # 2D matrix representation of timetables
    
    @classmethod
    def _initialize_data_structures(cls):
        """Initialize data structures with data from the database."""
        # Clear existing data structures
        cls._courses_linked_list = LinkedList()
        cls._faculty_schedule = {}
        cls._room_schedule = {}
        cls._timetable_matrix = {}
        
        # Load all courses
        courses = Course.query.all()
        for course in courses:
            # Add to linked list
            cls._courses_linked_list.add(course)
            
            # Add to faculty schedule hash table
            if course.faculty_id not in cls._faculty_schedule:
                cls._faculty_schedule[course.faculty_id] = {}
            cls._faculty_schedule[course.faculty_id][course.time_slot_id] = course
            
            # Add to room schedule hash table
            if course.room_id not in cls._room_schedule:
                cls._room_schedule[course.room_id] = {}
            cls._room_schedule[course.room_id][course.time_slot_id] = course
    
    @staticmethod
    def check_availability(faculty_id, room_id, time_slot_id):
        """
        Check if faculty and room are available for the given time slot.
        
        Args:
            faculty_id: ID of the faculty
            room_id: ID of the room
            time_slot_id: ID of the time slot
            
        Returns:
            bool: True if available, False if conflict exists
        """
        # Initialize data structures if needed
        if not TimetableScheduler._faculty_schedule:
            TimetableScheduler._initialize_data_structures()
        
        # Convert IDs to integers to ensure correct comparison
        faculty_id = int(faculty_id)
        room_id = int(room_id)
        time_slot_id = int(time_slot_id)
        
        # Check faculty availability using hash table
        faculty_conflict = False
        if faculty_id in TimetableScheduler._faculty_schedule:
            if time_slot_id in TimetableScheduler._faculty_schedule[faculty_id]:
                faculty_conflict = True
        
        # Check room availability using hash table
        room_conflict = False
        if room_id in TimetableScheduler._room_schedule:
            if time_slot_id in TimetableScheduler._room_schedule[room_id]:
                room_conflict = True
        
        # If both checks passed, the resources are available
        return not (faculty_conflict or room_conflict)

    @staticmethod
    def get_available_slots(faculty_id, room_id):
        """
        Get all available time slots for a given faculty and room.
        
        Args:
            faculty_id: ID of the faculty
            room_id: ID of the room
            
        Returns:
            list: List of available time slot objects
        """
        # Initialize data structures if needed
        if not TimetableScheduler._faculty_schedule:
            TimetableScheduler._initialize_data_structures()
        
        # Convert IDs to integers
        faculty_id = int(faculty_id)
        room_id = int(room_id)
        
        # Get all time slots
        all_time_slots = TimeSlot.query.all()
        
        # Use our hash tables to efficiently check availability
        faculty_busy_slots = set()
        if faculty_id in TimetableScheduler._faculty_schedule:
            faculty_busy_slots = set(TimetableScheduler._faculty_schedule[faculty_id].keys())
        
        room_busy_slots = set()
        if room_id in TimetableScheduler._room_schedule:
            room_busy_slots = set(TimetableScheduler._room_schedule[room_id].keys())
        
        # Combine all busy slots using set operations
        all_busy_slots = faculty_busy_slots.union(room_busy_slots)
        
        # Filter available slots in O(n) time using set membership test
        available_slots = []
        for time_slot in all_time_slots:
            if time_slot.id not in all_busy_slots:
                available_slots.append(time_slot)
        
        return available_slots

    @staticmethod
    def get_conflict_details(faculty_id, room_id, time_slot_id):
        """
        Get details about what's causing the conflict.
        
        Args:
            faculty_id: ID of the faculty
            room_id: ID of the room
            time_slot_id: ID of the time slot
            
        Returns:
            dict: Conflict details
        """
        # Initialize data structures if needed
        if not TimetableScheduler._faculty_schedule:
            TimetableScheduler._initialize_data_structures()
        
        # Convert IDs to integers
        faculty_id = int(faculty_id)
        room_id = int(room_id)
        time_slot_id = int(time_slot_id)
        
        conflict_details = {
            'faculty_conflict': False,
            'room_conflict': False,
            'faculty_course': None,
            'room_course': None,
            'course_name': None,
            'faculty_name': None
        }
        
        # Check faculty conflict - Using direct database query instead of cached object
        if faculty_id in TimetableScheduler._faculty_schedule:
            if time_slot_id in TimetableScheduler._faculty_schedule[faculty_id]:
                conflict_details['faculty_conflict'] = True
                # Get a fresh copy from the database instead of using potentially detached object
                faculty_course_id = TimetableScheduler._faculty_schedule[faculty_id][time_slot_id].id
                faculty_course = Course.query.get(faculty_course_id)
                conflict_details['faculty_course'] = faculty_course
                conflict_details['course_name'] = faculty_course.name
                conflict_details['faculty_name'] = faculty_course.instructor.name
        
        # Check room conflict - Using direct database query instead of cached object
        if room_id in TimetableScheduler._room_schedule:
            if time_slot_id in TimetableScheduler._room_schedule[room_id]:
                conflict_details['room_conflict'] = True
                # Get a fresh copy from the database instead of using potentially detached object
                room_course_id = TimetableScheduler._room_schedule[room_id][time_slot_id].id
                room_course = Course.query.get(room_course_id)
                conflict_details['room_course'] = room_course
                
                # If we don't have course info from faculty conflict, get it from room conflict
                if not conflict_details['course_name']:
                    conflict_details['course_name'] = room_course.name
                    conflict_details['faculty_name'] = room_course.instructor.name
        
        return conflict_details

    @staticmethod
    def schedule_course(faculty_id, division_id, room_id, time_slot_id, course_name):
        """
        Try to schedule a course at the specified time slot.
        
        Args:
            faculty_id: ID of the faculty
            division_id: ID of the division
            room_id: ID of the room
            time_slot_id: ID of the time slot
            course_name: Name of the course
            
        Returns:
            tuple: (success, message, Course object or None, conflict_details or None)
        """
        # Convert IDs to integers
        faculty_id = int(faculty_id)
        division_id = int(division_id)
        room_id = int(room_id)
        time_slot_id = int(time_slot_id)
        
        # Initialize data structures if needed
        if not TimetableScheduler._faculty_schedule:
            TimetableScheduler._initialize_data_structures()
            
        # Check for any conflicts (both faculty and room)
        is_available = TimetableScheduler.check_availability(faculty_id, room_id, time_slot_id)
        
        if is_available:
            # Create new course with the given parameters
            new_course = Course(
                name=course_name,
                faculty_id=faculty_id,
                division_id=division_id,
                room_id=room_id,
                time_slot_id=time_slot_id
            )
            db.session.add(new_course)
            db.session.commit()
            
            # Update our data structures
            TimetableScheduler._initialize_data_structures()  # Refresh all data structures
            
            return True, "Course scheduled successfully.", new_course, None
        else:
            # Get detailed conflict information to provide better feedback
            conflict_details = TimetableScheduler.get_conflict_details(faculty_id, room_id, time_slot_id)
            
            # Create specific error message based on conflict type
            if conflict_details['room_conflict']:
                conflict_message = "Room is already booked for this time slot. Please select from available time slots."
            elif conflict_details['faculty_conflict']:
                conflict_message = "You already have a class scheduled at this time. Please select from available time slots."
            else:
                conflict_message = "Scheduling conflict detected. Please select from available time slots."
            
            # NEVER auto-assign to another slot - always return the conflict for manual resolution
            return False, conflict_message, None, conflict_details

    @staticmethod
    def get_timetable_for_faculty(faculty_id):
        """
        Get the complete timetable for a specific faculty.
        
        Args:
            faculty_id: ID of the faculty
            
        Returns:
            dict: A 2D matrix representing the timetable
        """
        # Convert ID to integer
        faculty_id = int(faculty_id)
        
        # Create a 2D matrix for the timetable (days x time slots)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = TimeSlot.query.distinct(TimeSlot.start_time, TimeSlot.end_time).all()
        
        # Initialize the 2D matrix with empty values
        timetable = {}
        for day in days:
            timetable[day] = {}
            for slot in time_slots:
                if slot.day == day:
                    time_key = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
                    timetable[day][time_key] = None
        
        # Get all courses for the faculty using direct query (not linked list)
        courses = Course.query.filter_by(faculty_id=faculty_id).all()
        
        # Fill the timetable with courses
        for course in courses:
            day = course.time_slot.day
            time_key = f"{course.time_slot.start_time.strftime('%H:%M')}-{course.time_slot.end_time.strftime('%H:%M')}"
            
            course_info = {
                'id': course.id,
                'name': course.name,
                'room': course.room.name,
                'division': course.division.name
            }
            
            timetable[day][time_key] = course_info
        
        # Store in class-level matrix
        TimetableScheduler._timetable_matrix[f"faculty_{faculty_id}"] = timetable
        
        return timetable

    @staticmethod
    def get_timetable_for_division(division_id):
        """
        Get the complete timetable for a specific student division.
        
        Args:
            division_id: ID of the division
            
        Returns:
            dict: A 2D matrix representing the timetable
        """
        # Convert ID to integer
        division_id = int(division_id)
        
        # Create a 2D matrix for the timetable (days x time slots)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = TimeSlot.query.distinct(TimeSlot.start_time, TimeSlot.end_time).all()
        
        # Initialize the 2D matrix with empty values
        timetable = {}
        for day in days:
            timetable[day] = {}
            for slot in time_slots:
                if slot.day == day:
                    time_key = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
                    timetable[day][time_key] = None
        
        # Get all courses for the division using direct query
        courses = Course.query.filter_by(division_id=division_id).all()
        
        # Fill the timetable with courses
        for course in courses:
            day = course.time_slot.day
            time_key = f"{course.time_slot.start_time.strftime('%H:%M')}-{course.time_slot.end_time.strftime('%H:%M')}"
            
            course_info = {
                'id': course.id,
                'name': course.name,
                'room': course.room.name,
                'faculty': course.instructor.name
            }
            
            timetable[day][time_key] = course_info
        
        # Store in class-level matrix
        TimetableScheduler._timetable_matrix[f"division_{division_id}"] = timetable
        
        return timetable