/**
 * Custom Application Scripts
 * Use this file for your page-specific logic, event listeners, and custom UI interactions.
 */

$(document).ready(function () {
    
    // Initialize Bootstrap tooltips globally if they exist on the page
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Add generic confirmation dialogs using SweetAlert2
    // Usage: Add class 'btn-delete-confirm' to any delete button
    $(document).on('click', '.btn-delete-confirm', function(e) {
        e.preventDefault();
        const formToSubmit = $(this).closest('form');
        
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#9b2c2c', // LTCATO Primary Red
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed && formToSubmit.length) {
                formToSubmit.submit();
            }
        });
    });

    console.log("LTCATO Main Scripts loaded successfully.");
});