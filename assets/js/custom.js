document.addEventListener("DOMContentLoaded", function() {
  let introOverlay = document.getElementById("intro-overlay");
  let mainContent = document.querySelector(".fade-in-hidden");

  setTimeout(() => {
      introOverlay.style.opacity = "0"; // Fade out intro
      setTimeout(() => {
          introOverlay.style.display = "none"; // Remove after fade out
          mainContent.style.opacity = "1"; // Show main content
      }, 1500); // Match fade-out duration
  }, 1000); // Intro text stays visible for 2 seconds
});