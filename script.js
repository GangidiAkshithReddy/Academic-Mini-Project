document.addEventListener('DOMContentLoaded', function() {
    const symptomForm = document.querySelector('form');
    
    symptomForm.addEventListener('submit', async (e) => {
        e.preventDefault();  // Prevent the default form submission

        const symptom = document.getElementById("symptoms").value;
        
        // Basic validation
        if (!symptom.trim()) {
            alert("Please enter your symptoms.");
            return;
        }

        // Make an asynchronous POST request to submit the symptom data
        const response = await fetch("/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ symptoms: symptom })
        });

        // Parse the response as text (since you are rendering HTML)
        const data = await response.text();

        // Find the container to update with the new data
        document.querySelector('.container').innerHTML = data;
    });
});
