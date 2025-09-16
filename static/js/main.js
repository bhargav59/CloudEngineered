// Main JavaScript file for CloudEngineered
document.addEventListener('DOMContentLoaded', function() {
    console.log('CloudEngineered JS loaded successfully');
    
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // User dropdown toggle
    const userDropdownButton = document.querySelector('.user-dropdown-button');
    const userDropdownMenu = document.querySelector('.user-dropdown-menu');
    
    if (userDropdownButton && userDropdownMenu) {
        userDropdownButton.addEventListener('click', function() {
            userDropdownMenu.classList.toggle('hidden');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!userDropdownButton.contains(event.target) && !userDropdownMenu.contains(event.target)) {
                userDropdownMenu.classList.add('hidden');
            }
        });
    }
});