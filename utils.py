# utils.py
from models import db, Course, Faculty, Room, TimeSlot, Division
from collections import defaultdict

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
    
    def remove(self, course_id):
        """Remove a course from the linked list by course ID."""
        if not self.head:
            return False
        
        # If head is the course to remove
        if self.head.course.id == course_id:
            self.head = self.head.next
            return True
        
        # Search for the course
        current = self.head
        while current.next and current.next.course.id != course_id:
            current = current.next
        
        # If found, remove it
        if current.next:
            current.next = current.next.next
            return True
        
        return False

class ConflictGraph:
    """Graph representation for detecting scheduling conflicts using graph coloring."""
    
    def __init__(self):
        """Initialize an empty graph."""
        # Adjacency list representation of the graph
        # Each vertex (course_id) maps to a list of adjacent vertices (conflicting courses)
        self.graph = defaultdict(list)
        # Map of course IDs to their corresponding Course objects
        self.courses = {}
    
    def add_vertex(self, course):
        """Add a course as a vertex to the graph if it doesn't exist."""
        if course.id not in self.courses:
            self.courses[course.id] = course
            self.graph[course.id] = []
    
    def add_edge(self, course1_id, course2_id):
        """Add an edge between two courses indicating they conflict."""
        if course2_id not in self.graph[course1_id]:
            self.graph[course1_id].append(course2_id)
        if course1_id not in self.graph[course2_id]:
            self.graph[course2_id].append(course1_id)
    
    def build_from_courses(self, courses):
        """Build the conflict graph from a list of courses."""
        # Reset the graph
        self.graph = defaultdict(list)
        self.courses = {}
        
        # Add all courses as vertices
        for course in courses:
            self.add_vertex(course)
        
        # Add edges between conflicting courses
        for i, course1 in enumerate(courses):
            for j in range(i + 1, len(courses)):
                course2 = courses[j]
                
                # Check if courses conflict (same time slot and same faculty, room, or division)
                if course1.time_slot_id == course2.time_slot_id:
                    if (course1.faculty_id == course2.faculty_id or  # Same faculty
                        course1.room_id == course2.room_id or        # Same room
                        course1.division_id == course2.division_id): # Same division
                        self.add_edge(course1.id, course2.id)
    
    def would_create_conflict(self, new_course):
        """
        Check if adding a new course would create a conflict.
        
        Args:
            new_course: The course to check
            
        Returns:
            bool: True if conflict would be created, False otherwise
        """
        # Check conflicts with existing courses
        for course_id, course in self.courses.items():
            if course.time_slot_id == new_course.time_slot_id:
                if (course.faculty_id == new_course.faculty_id or
                    course.room_id == new_course.room_id or
                    course.division_id == new_course.division_id):
                    return True
        
        return False
    
    def get_conflicting_courses(self, new_course):
        """
        Get all courses that would conflict with the new course.
        
        Args:
            new_course: The course to check
            
        Returns:
            list: List of Course objects that conflict with the new course
        """
        conflicts = []
        for course_id, course in self.courses.items():
            if course.time_slot_id == new_course.time_slot_id:
                if (course.faculty_id == new_course.faculty_id or
                    course.room_id == new_course.room_id or
                    course.division_id == new_course.division_id):
                    conflicts.append(course)
        
        return conflicts
    
    def is_valid_coloring(self):
        """
        Check if the current graph has a valid coloring (no conflicts).
        
        Returns:
            bool: True if valid, False otherwise
        """
        for course_id, neighbors in self.graph.items():
            course = self.courses[course_id]
            for neighbor_id in neighbors:
                neighbor = self.courses[neighbor_id]
                if course.time_slot_id == neighbor.time_slot_id:
                    # Two adjacent courses have the same color (time slot)
                    return False
        
        return True

class TimetableScheduler:
    """Handles the core scheduling logic for the timetable system."""
    
    # Class-level data structures
    _courses_linked_list = LinkedList()
    _faculty_schedule = {}  # Hash table for faculty schedules
    _room_schedule = {}     # Hash table for room schedules
    _timetable_matrix = {}  # 2D matrix representation of timetables
    _conflict_graph = ConflictGraph()  # Graph for conflict detection
    
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
        
        # Build the conflict graph
        cls._conflict_graph.build_from_courses(courses)
    
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
        
        # Create a temporary course object to check for conflicts
        # Note: We don't save this to the database, it's just for checking
        temp_course = type('TempCourse', (), {
            'id': -1,
            'name': "temp",
            'faculty_id': faculty_id,
            'division_id': 1,  # Arbitrary division for conflict check
            'room_id': room_id,
            'time_slot_id': time_slot_id
        })
        
        # Use graph coloring to check for conflicts
        if TimetableScheduler._conflict_graph.would_create_conflict(temp_course):
            return False
        
        return True

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
        
        # Create a temporary course object for conflict checking
        temp_course = type('TempCourse', (), {
            'id': -1,
            'name': "temp",
            'faculty_id': faculty_id,
            'division_id': 1,
            'room_id': room_id,
            'time_slot_id': time_slot_id
        })
        
        # Use graph to get conflicting courses
        conflicts = TimetableScheduler._conflict_graph.get_conflicting_courses(temp_course)
        
        for conflict in conflicts:
            # Check if it's a faculty conflict
            if conflict.faculty_id == faculty_id:
                conflict_details['faculty_conflict'] = True
                conflict_details['faculty_course'] = conflict
                conflict_details['course_name'] = conflict.name
                # Get fresh faculty name from database to avoid detached instance errors
                faculty = Faculty.query.get(conflict.faculty_id)
                conflict_details['faculty_name'] = faculty.name if faculty else "Unknown"
            
            # Check if it's a room conflict
            if conflict.room_id == room_id:
                conflict_details['room_conflict'] = True
                conflict_details['room_course'] = conflict
                
                # If we don't have course info from faculty conflict, get it from room conflict
                if not conflict_details['course_name']:
                    conflict_details['course_name'] = conflict.name
                    faculty = Faculty.query.get(conflict.faculty_id)
                    conflict_details['faculty_name'] = faculty.name if faculty else "Unknown"
        
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
            
        # Create a temporary course object to check for conflicts using graph coloring
        temp_course = type('TempCourse', (), {
            'id': -1,
            'name': course_name,
            'faculty_id': faculty_id,
            'division_id': division_id,
            'room_id': room_id,
            'time_slot_id': time_slot_id
        })
        
        # Use graph coloring to check for conflicts
        if TimetableScheduler._conflict_graph.would_create_conflict(temp_course):
            # Get detailed conflict information
            conflict_details = TimetableScheduler.get_conflict_details(faculty_id, room_id, time_slot_id)
            
            # Create specific error message based on conflict type
            if conflict_details['room_conflict']:
                conflict_message = "Room is already booked for this time slot. Please select from available time slots."
            elif conflict_details['faculty_conflict']:
                conflict_message = "You already have a class scheduled at this time. Please select from available time slots."
            else:
                conflict_message = "Scheduling conflict detected. Please select from available time slots."
            
            return False, conflict_message, None, conflict_details
        else:
            # No conflicts, create and save the course
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
            TimetableScheduler._initialize_data_structures()
            
            return True, "Course scheduled successfully.", new_course, None

    @staticmethod
    def get_timetable_for_faculty(faculty_id):
        """
        Get the complete timetable for a specific faculty using the 2D matrix.
        
        Args:
            faculty_id: ID of the faculty
            
        Returns:
            dict: A 2D matrix representing the timetable
        """
        # Convert ID to integer
        faculty_id = int(faculty_id)
        
        # Get all courses for the faculty using direct query
        courses = Course.query.filter_by(faculty_id=faculty_id).all()
        
        # Build the 2D timetable matrix
        timetable = TimetableScheduler.build_timetable_matrix(courses)
        
        # Process the timetable for the template format
        processed_timetable = {}
        for day, time_slots in timetable.items():
            processed_timetable[day] = {}
            for time_key, course in time_slots.items():
                if course:
                    processed_timetable[day][time_key] = {
                        'id': course.id,
                        'name': course.name,
                        'room': course.room.name,
                        'division': course.division.name
                    }
                else:
                    processed_timetable[day][time_key] = None
        
        # Store in class-level matrix
        TimetableScheduler._timetable_matrix[f"faculty_{faculty_id}"] = processed_timetable
        
        return processed_timetable

    @staticmethod
    def get_timetable_for_division(division_id):
        """
        Get the complete timetable for a specific student division using the 2D matrix.
        
        Args:
            division_id: ID of the division
            
        Returns:
            dict: A 2D matrix representing the timetable
        """
        # Convert ID to integer
        division_id = int(division_id)
        
        # Get all courses for the division using direct query
        courses = Course.query.filter_by(division_id=division_id).all()
        
        # Build the 2D timetable matrix
        timetable = TimetableScheduler.build_timetable_matrix(courses)
        
        # Process the timetable for the template format
        processed_timetable = {}
        for day, time_slots in timetable.items():
            processed_timetable[day] = {}
            for time_key, course in time_slots.items():
                if course:
                    processed_timetable[day][time_key] = {
                        'id': course.id,
                        'name': course.name,
                        'room': course.room.name,
                        'faculty': course.instructor.name
                    }
                else:
                    processed_timetable[day][time_key] = None
        
        # Store in class-level matrix
        TimetableScheduler._timetable_matrix[f"division_{division_id}"] = processed_timetable
        
        return processed_timetable

    @staticmethod
    def build_timetable_matrix(courses, day_order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']):
        """
        Build a 2D matrix representation of timetable from courses.
        
        Args:
            courses: List of course objects
            day_order: Order of days to display
            
        Returns:
            dict: A 2D matrix representing the timetable
        """
        # Get all unique time slots
        time_slots = TimeSlot.query.all()
        
        # Create a mapping of day -> start_time -> end_time -> slot_id
        time_slot_map = {}
        for slot in time_slots:
            if slot.day not in time_slot_map:
                time_slot_map[slot.day] = {}
                
            start_time_str = slot.start_time.strftime('%H:%M')
            end_time_str = slot.end_time.strftime('%H:%M')
            time_key = f"{start_time_str}-{end_time_str}"
            
            if time_key not in time_slot_map[slot.day]:
                time_slot_map[slot.day][time_key] = slot.id
        
        # Initialize 2D matrix
        timetable = {}
        for day in day_order:
            if day in time_slot_map:
                timetable[day] = {}
                for time_key in sorted(time_slot_map[day].keys()):
                    timetable[day][time_key] = None
        
        # Fill matrix with courses
        for course in courses:
            day = course.time_slot.day
            start_time_str = course.time_slot.start_time.strftime('%H:%M')
            end_time_str = course.time_slot.end_time.strftime('%H:%M')
            time_key = f"{start_time_str}-{end_time_str}"
            
            if day in timetable and time_key in timetable[day]:
                timetable[day][time_key] = course
        
        return timetable