/**
 * System Utility Scripts for LTCATO Dashboard
 * This extends jQuery with helper functions used across the application.
 */

(function ($) {
    "use strict";

    // Define the SystemScript namespace on jQuery
    $.SystemScript = {
        
        /**
         * Formats a raw date/time string from the database into a human-readable format.
         * Example: "2023-10-25T14:30:00Z" -> "Oct 25, 2023, 2:30 PM"
         * * @param {string} dateString - The raw datetime string (e.g., from Supabase)
         * @returns {string} - The formatted date string
         */
        dateTimeFormat: function (dateString) {
            if (!dateString) return "";
            
            const date = new Date(dateString);
            
            // Return original string if invalid date
            if (isNaN(date.getTime())) return dateString;

            const options = { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit', 
                minute: '2-digit'
            };
            
            return date.toLocaleDateString('en-US', options);
        },

        /**
         * Helper for DataTables to get the default sorting column.
         * It looks through the table headers (<th>) to find a match for the column name.
         * * @param {string} tableSelector - The CSS selector for the table element
         * @param {string} columnName - The data-col attribute or lowercase text of the header
         * @param {string} direction - Sorting direction ('asc' or 'desc')
         * @returns {Array} - DataTable order array format (e.g., [[0, 'desc']])
         */
        getDefaultOrder: function (tableSelector, columnName, direction = 'desc') {
            let colIndex = 0; // Default to the very first column
            
            if (columnName) {
                // Look for the specific column in the table header
                $(tableSelector).find('thead th').each(function(index) {
                    const dataCol = $(this).attr('data-col');
                    const textCol = $(this).text().trim().toLowerCase().replace(/\s+/g, '_');
                    
                    if (dataCol === columnName || textCol === columnName) {
                        colIndex = index;
                        return false; // Break the jQuery each loop
                    }
                });
            }
            
            return [[colIndex, direction]];
        }
        
    };

})(jQuery);