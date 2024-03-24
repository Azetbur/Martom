document.addEventListener("DOMContentLoaded", function() {
    const toggleDropdown = (event) => {
        const container = event.currentTarget.querySelector('.options-container');
        const isActive = container.classList.contains('active');
        // Hide all active containers first
        document.querySelectorAll('.options-container.active').forEach(activeContainer => {
            activeContainer.classList.remove('active');
        });
        // Then toggle the current container, if it was not already active
        if (!isActive) {
            container.classList.add('active');
        }
        event.stopPropagation(); // Prevent the click from immediately closing the dropdown
    };

    // Populate and setup hour picker
    const customHourPicker = document.getElementById('customHourPicker');
    const hoursContainer = customHourPicker.querySelector('.options-container');
    for (let i = 0; i < 24; i++) {
        const hourOption = document.createElement('div');
        hourOption.classList.add('option');
        hourOption.textContent = i < 10 ? '0' + i : i;
        hourOption.addEventListener('click', function(event) {
            customHourPicker.querySelector('.selected-value').textContent = this.textContent;
            hoursContainer.classList.remove('active');
            event.stopPropagation(); // Stop propagation to document click listener
        });
        hoursContainer.appendChild(hourOption);
    }

    // Populate and setup minute picker
    const customMinutePicker = document.getElementById('customMinutePicker');
    const minutesContainer = customMinutePicker.querySelector('.options-container');
    for (let i = 0; i < 60; i += 5) {
        const minuteOption = document.createElement('div');
        minuteOption.classList.add('option');
        minuteOption.textContent = i < 10 ? '0' + i : i;
        minuteOption.addEventListener('click', function(event) {
            customMinutePicker.querySelector('.selected-value').textContent = this.textContent;
            minutesContainer.classList.remove('active');
            event.stopPropagation(); // Stop propagation to document click listener
        });
        minutesContainer.appendChild(minuteOption);
    }

    // Setup click listeners for showing dropdowns
    [customHourPicker, customMinutePicker].forEach(picker => {
        picker.querySelector('.selected-value').addEventListener('click', toggleDropdown);
    });

    // Close options when clicking outside
    document.addEventListener('click', function() {
        document.querySelectorAll('.options-container.active').forEach(activeContainer => {
            activeContainer.classList.remove('active');
        });
    });
});
