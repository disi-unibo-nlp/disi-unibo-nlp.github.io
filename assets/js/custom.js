/* document.addEventListener("DOMContentLoaded", function () {
  let introOverlay = document.getElementById("intro-overlay");
  let mainContent = document.querySelector(".fade-in-hidden");

  setTimeout(() => {
      introOverlay.classList.add("fade-out");

      setTimeout(() => {
          introOverlay.style.display = "none"; // Fully remove it after fading out
          mainContent.style.opacity = "1"; // Show main content
      }, 600); // Ensure it matches the CSS transition duration
  }, 600); // Keep the intro visible for 1 second before fading out
}); */

document.addEventListener("DOMContentLoaded", function () {
  let introOverlay = document.getElementById("intro-overlay");
  let mainContent = document.querySelector(".fade-in-hidden");

  setTimeout(() => {
      // Start the overlay fade effect
      introOverlay.classList.add("intro-overlay-fade");

      setTimeout(() => {
          introOverlay.style.display = "none"; // Fully remove it after animation
          mainContent.style.opacity = "1"; // Show main content
      }, 1000); // Matches animation duration
  }, 600); // Keep the intro visible for 1 second before fading
});