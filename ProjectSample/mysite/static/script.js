document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent form submission
    
    // Get form values
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    
    // Perform login validation
    if (username === "admin" && password === "password") {
      alert("Login successful!");
    } else {
      alert("Invalid username or password.");
    }
  });
  