<!DOCTYPE html>
<html lang="en">
    <head>
        <title> The Matrix</title>
    </head>
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">

    <body>

    <div class = "w3-center w3-top">
        <h1> The Matrix </h1>
    </div>
        <div class = "w3-bottom">
            <form action="#">
                <input type= "text" id = "userprompt" placeholder= "Ask the matrix a question today!">
                <input type = "submit" id= "btn" value = "Send now!">
                <div id= "result"></div>
            </form>
</div>
<script>
    document.getElementById('btn').addEventListener("click", function()
    {
        // get value from text input 
        const userInput = document.getElementById('userprompt').value;
        // send user input to the api 
        fetch("http://127.0.0.1:5000/regbutton", {
            method: "POST",
            headers: {
                "Content-type": "application/json"
            },
            body: JSON.stringify({message: userInput}) // input value will be in the string message
        })
        .then(response => resonse.json())
        .then(data => console.log("Success:", data))
        .catch(error => console.error("Error:", error));

    });
    </script>
    </body>
</html>
