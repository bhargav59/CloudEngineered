// CloudEngineered Platform - Main JavaScript
console.log('CloudEngineered platform loaded');

// Enhanced search functionality
document.addEventListener('DOMContentLoaded', function() {
    // Search form enhancement
    const searchInput = document.getElementById('hero-search');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('ring-4', 'ring-blue-300', 'ring-opacity-50');
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('ring-4', 'ring-blue-300', 'ring-opacity-50');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add hover effects to cards
    document.querySelectorAll('.card, .bg-white').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Newsletter form handling
    const newsletterForm = document.querySelector('form[action*="newsletter"]');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            const email = this.querySelector('input[name="email"]');
            if (email && !email.value.includes('@')) {
                e.preventDefault();
                alert('Please enter a valid email address');
                email.focus();
            }
        });
    }
    
    // Add loading animation to buttons
    document.querySelectorAll('button[type="submit"], .btn-primary').forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit') {
                this.style.opacity = '0.7';
                this.textContent = 'Loading...';
            }
        });
    });
});

// Performance monitoring
if (window.performance && window.performance.timing) {
    window.addEventListener('load', function() {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log('Page load time:', loadTime + 'ms');
    });
}