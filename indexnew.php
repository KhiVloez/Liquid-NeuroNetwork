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
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
        }
        .container {
            width: 50%;
            margin: auto;
            padding: 20px;
            background-color: #f4f4f4;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            margin-top: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            color: black; /* Ensures text is visible */
        }
        button {
            margin-top: 10px;
            padding: 10px 15px;
            border: none;
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        #result {
            margin-top: 20px;
            font-weight: bold;
        }
    </style>
</head>

<body>

    <div class="container">
        <h1>The Matrix Connection</h1>
        <form id="matrixForm">
            <input type="text" id="userprompt" name="userprompt" placeholder="Ask the Matrix a question today!" required>
            <button type="submit" id="btn">Send now!</button>
            <div id="result"></div>
        </form>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function() {
            console.log("Page loaded, JavaScript active."); // Debugging

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
                fetch("indexnew.php", {
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
        });
    </script>

</body>
</html>
