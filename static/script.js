/* static/script.js */
function openTab(tabId) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Show the selected tab content
    document.getElementById(tabId).classList.add('active');
    
    // Add active class to the clicked button
    const activeButton = document.querySelector(`[onclick="openTab('${tabId}')"]`);
    activeButton.classList.add('active');
}

// Function to initialize time slot highlighting
function initTimeSlotHighlight() {
    const courseSlots = document.querySelectorAll('.course-slot');
    
    courseSlots.forEach(slot => {
        slot.addEventListener('mouseenter', function() {
            if (!this.classList.contains('empty')) {
                this.style.boxShadow = '0 0 10px rgba(52, 152, 219, 0.5)';
            }
        });
        
        slot.addEventListener('mouseleave', function() {
            this.style.boxShadow = 'none';
        });
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab functionality if we're on the index page
    const tabsContainer = document.querySelector('.tabs');
    if (tabsContainer) {
        // Check if we have flashed messages and we're in the login tab
        const flashedMessages = document.querySelector('.alert');
        if (flashedMessages && flashedMessages.parentElement.id === 'login-tab') {
            openTab('login-tab');
        }
    }
    
    // Initialize time slot highlighting
    initTimeSlotHighlight();
});