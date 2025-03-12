/* document.addEventListener("DOMContentLoaded", function () {
  let introOverlay = document.getElementById("intro-overlay");
  let mainContent = document.querySelector(".fade-in-hidden");

  setTimeout(() => {
      // Start the overlay fade effect
      introOverlay.classList.add("intro-overlay-fade");

      introOverlay.style.display = "none"; // Fully remove it after animation
      mainContent.style.opacity = "1"; // Show main content
  }, 1000); // Keep the intro visible for 1 second before fading
}); */

document.addEventListener("DOMContentLoaded", function () {
  setTimeout(() => {
      let logo1 = document.getElementById("intro-logo"); // First logo
      let logo2 = document.getElementById("intro-logo2"); // Second logo
      let overlay = document.getElementById("intro-overlay");

      // Determine scale based on screen size
      let scaleValue = window.innerWidth < 768 ? "1" : "1.5"; // Mobile: scale(1), Desktop: scale(1.5)

      // Fade out the first logo after animation
      logo1.style.opacity = "0";
      logo1.style.transform = `scale(${scaleValue})`; // Keep zoomed

      // Fade in second logo with responsive scaling
      setTimeout(() => {
          logo2.style.opacity = "1";
          logo2.style.transform = `scale(${scaleValue})`; // Adjusts for mobile vs. desktop
      }, 300); // Small delay to make the transition smoother

      // Remove overlay after transition
      setTimeout(() => {
          overlay.style.opacity = "0";
          setTimeout(() => {
              overlay.style.display = "none";
          }, 400); // Give a bit of delay before removing it completely
      }, 1600);
  }, 600); // Initial delay
});
