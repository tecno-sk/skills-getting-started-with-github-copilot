// Global variables and functions
let activitiesList, activitySelect, signupForm, messageDiv;

// Function to fetch activities from API
async function fetchActivities() {
  try {
    const response = await fetch("/activities");
    const activities = await response.json();

    // Clear loading message
    activitiesList.innerHTML = "";
    
    // Clear activity select options (keep the first default option)
    activitySelect.innerHTML = '<option value="">Select an activity</option>';

    // Populate activities list
    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <p><strong>Schedule:</strong> ${details.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <div class="participants-section">
          <strong>Current Participants:</strong>
          ${details.participants.length > 0 ? 
            `<div class="participants-list">
                ${details.participants.map(participant => `
                  <div class="participant-item">
                    <span class="participant-email">${participant}</span>
                    <button class="delete-btn" onclick="unregisterParticipant('${name}', '${participant}')" title="Unregister participant">
                      ✕
                    </button>
                  </div>
                `).join('')}
            </div>` : 
            '<p class="no-participants">No participants yet</p>'
          }
        </div>
      `;

      activitiesList.appendChild(activityCard);

      // Add option to select dropdown
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  } catch (error) {
    activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
    console.error("Error fetching activities:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Initialize DOM element references
  activitiesList = document.getElementById("activities-list");
  activitySelect = document.getElementById("activity");
  signupForm = document.getElementById("signup-form");
  messageDiv = document.getElementById("message");

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities list to show updated participant count
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});

// Function to unregister a participant from an activity
async function unregisterParticipant(activityName, email) {
  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Show success message
      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");

      // Hide message after 3 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 3000);

      // Refresh the activities list to reflect the change
      await fetchActivities();
    } else {
      // Show error message
      messageDiv.textContent = result.detail || "An error occurred while unregistering";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    }
  } catch (error) {
    console.error("Error unregistering participant:", error);
    messageDiv.textContent = "Failed to unregister participant. Please try again.";
    messageDiv.className = "error";
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }
}
