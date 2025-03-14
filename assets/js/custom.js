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
    const logo1 = document.getElementById("intro-logo"); 
    const logo2 = document.getElementById("intro-logo2"); 
    const overlay = document.getElementById("intro-overlay");

    setTimeout(() => {
        logo1.style.opacity = "0";     
        logo2.style.opacity = "1";

        setTimeout(() => {
            overlay.style.opacity = "0";   

            setTimeout(() => {
                overlay.style.display = "none";
            }, 1000); 
        }, 1300);
    }, 1000);
});