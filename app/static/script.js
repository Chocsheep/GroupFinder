document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.notification .delete');

    deleteButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const notification = button.closest('.notification');
            
            if (notification) {
                notification.remove();
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    // Existing notification removal code can stay right above this...

    // --- Theme Toggle Logic ---
    const toggleBtn = document.getElementById('theme-toggle');
    const toggleIcon = document.getElementById('theme-toggle-icon');
    const rootHtml = document.documentElement; // Targets the <html> element

    // 1. Check if the user has a saved preference from a previous visit
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Set the initial state based on storage
    rootHtml.setAttribute('data-theme', savedTheme);
    updateToggleIcon(savedTheme);

    // 2. Listen for clicks on the toggle button
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            // Determine the next theme
            const currentTheme = rootHtml.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            // Apply the new theme to the document
            rootHtml.setAttribute('data-theme', newTheme);
            
            // Save it so it remembers on next page load
            localStorage.setItem('theme', newTheme);
            
            // Swap out the moon/sun icons
            updateToggleIcon(newTheme);
        });
    }

    // Helper function to update the icon appearance cleanly
    function updateToggleIcon(theme) {
        if (!toggleIcon) return;
        if (theme === 'dark') {
            toggleIcon.className = 'fa fa-sun-o'; // Show sun icon in dark mode
        } else {
            toggleIcon.className = 'fa fa-moon-o'; // Show moon icon in light mode
        }
    }
});