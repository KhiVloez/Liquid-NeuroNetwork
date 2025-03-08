<?php
// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Handle the POST request from JavaScript
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $url = "http://127.0.0.1:5000/regbutton"; // Flask API URL

    // Retrieve JSON input from JavaScript fetch request
    $json_data = file_get_contents("php://input"); 

    // Debugging: Log the received JSON
    file_put_contents("debug_log.txt", "Received JSON: " . $json_data . "\n", FILE_APPEND);

    // Set up HTTP request options
    $options = [
        "http" => [
            "header"  => "Content-Type: application/json",
            "method"  => "POST",
            "content" => $json_data
        ]
    ];

    // Create context for HTTP request
    $context = stream_context_create($options);

    // Send the request and capture the response
    $result = file_get_contents($url, false, $context);

    // Debugging: Log Flask response
    file_put_contents("debug_log.txt", "Flask Response: " . $result . "\n", FILE_APPEND);

    // Return the Flask response back to the frontend
    echo $result;
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <title>The Matrix Connection</title>
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
</head>

<body>

    <div class="w3-center w3-top">
        <h1>The Matrix Connection</h1>
    </div>

    <div class="w3-container w3-center">
        <form id="matrixForm">
            <input type="text" id="userprompt" placeholder="Ask the Matrix a question today!" class="w3-input w3-border">
            <button type="submit" id="btn" class="w3-button w3-green w3-margin-top">Send now!</button>
            <div id="result" class="w3-panel w3-light-gray w3-padding w3-margin-top"></div>
        </form>
    </div>

    <script>
        document.getElementById("matrixForm").addEventListener("submit", function(event) {
            event.preventDefault(); // ✅ Prevents page refresh

            // Get value from text input
            const userInput = document.getElementById("userprompt").value.trim(); // ✅ Ensures no blank spaces

            // Debugging: Print user input before sending
            console.log("User Input:", userInput);

            // Ensure user input is not empty
            if (!userInput) {
                document.getElementById("result").innerText = "Please enter a question!";
                return;
            }

            // Send user input to PHP, which then forwards it to Flask
            fetch("index.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ input_data: userInput }) // ✅ Flask expects "input_data"
            })
            .then(response => response.json()) // ✅ Convert response to JSON
            .then(data => {
                console.log("Success:", data); // ✅ Log API response
                document.getElementById("result").innerText = data.message || data.error; // ✅ Display response
            })
            .catch(error => console.error("Error:", error));
        });
    </script>

</body>
</html>
