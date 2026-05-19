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