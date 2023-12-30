var selectedTracks = [];

$(document).ready(function() {
    // Create an empty list to store the selected tracks


    // Add a click event to each grid item
    $('.grid-item').click(function() {
        // Get the track ID from the id attribute
        var trackID = $(this).attr('id');

        // Check if the track is already in the selectedTracks array
        var index = selectedTracks.indexOf(trackID);
        if (selectedTracks.length >= 5 && index === -1) {
            alert("You can only select 5 tracks!");
            return;
        }
        else {
            if (index === -1) {
                // If the track is not in the array, add it
                selectedTracks.push(trackID);

                // Add a 'selected' class to the grid item
                $(this).addClass('selected');
            } else {
                // If the track is in the array, remove it
                selectedTracks.splice(index, 1);

                // Remove the 'selected' class from the grid item
                $(this).removeClass('selected');
            }
        }

        // Update the counter
        $('#counter').text(selectedTracks.length + "/5 artists picked");

        // For debugging, log the selectedTracks list to the console
        console.log(selectedTracks);
    });
});

$('#generate-button').click(function() {
    // Convert the selectedTracks array into a JSON string
    var json = JSON.stringify(selectedTracks);

    // Send a POST request to the server
    $.ajax({
        url: '/process_tracks',
        method: 'POST',
        data: json,
        contentType: 'application/json',
        success: function() {
            // Redirect to the /generate_audio page
            window.location.href = '/generate_audio';
        }
    });
});

$('#sign-in-button').click(function() {
    window.location.href = '/login';
});

$('#sign-out-button').click(function() {
    window.location.href = '/logout';
});