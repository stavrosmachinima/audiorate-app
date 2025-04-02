document.addEventListener("DOMContentLoaded", function () {
  // Find all rating containers
  const ratingContainers = document.querySelectorAll(".rating-container");
  const starCount = 5; // Total number of stars

  ratingContainers.forEach((container) => {
    const rateitRange = container.querySelector(".rateit-range");
    const rateitSelected = container.querySelector(".rateit-selected");
    const rateitHover = container.querySelector(".rateit-hover");
    const hiddenInput = container.querySelector('input[type="hidden"]');

    // Get the width of each star dynamically
    function getStarWidth() {
      return rateitRange.offsetWidth / starCount;
    }

    let starWidthPx = getStarWidth(); // Initial calculation of star width

    // Calculate star value from mouse position
    function getStarValueFromPosition(position) {
      const halfStarWidth = starWidthPx / 2;
      // Calculate which half-star increment we're on
      let starValue = Math.ceil(position / halfStarWidth) / 2;
      return Math.max(0.5, Math.min(starCount, starValue));
    }

    // Update the visual display based on star value
    function updateRatingDisplay(element, starValue, showElement = true) {
      // Recalculate star width to ensure it's current
      starWidthPx = getStarWidth();
      element.style.width = `${starValue * starWidthPx}px`;
      element.style.display = showElement ? "block" : "none";
    }

    // Handle mouse movement over rating area
    rateitRange.addEventListener("mousemove", function (e) {
      const position = e.clientX - this.getBoundingClientRect().left;
      const starValue = getStarValueFromPosition(position);
      console.log(`Star Value: ${starValue}`); // Debugging line
      updateRatingDisplay(rateitHover, starValue);
    });

    // Handle mouse leaving the rating area
    rateitRange.addEventListener("mouseleave", function () {
      rateitHover.style.display = "none";
    });

    // Handle click to set rating
    rateitRange.addEventListener("click", function (e) {
      const position = e.clientX - this.getBoundingClientRect().left;
      const starValue = getStarValueFromPosition(position);

      // Update selected width
      updateRatingDisplay(rateitSelected, starValue);

      // Update hidden input with the selected value
      hiddenInput.value = starValue;

      // Update ARIA attributes
      this.setAttribute("aria-valuenow", starValue * 2); // 0-10 range for ARIA
    });

    // Initialize any pre-existing ratings
    if (hiddenInput.value) {
      const starValue = parseFloat(hiddenInput.value);
      updateRatingDisplay(rateitSelected, starValue);
    }
  });

  // Handle window resize - adjust ratings based on new container widths
  window.addEventListener(
    "resize",
    function () {
      ratingContainers.forEach((container) => {
        const rateitRange = container.querySelector(".rateit-range");
        const rateitSelected = container.querySelector(".rateit-selected");
        const hiddenInput = container.querySelector('input[type="hidden"]');
        const starValue = parseFloat(hiddenInput.value) || 0;
        const starWidthPx = rateitRange.offsetWidth / starCount;

        // Keep the same star value but adjust to new container width
        rateitSelected.style.width = `${starValue * starWidthPx}px`;
      });
    },
    { passive: true }
  ); // Add passive flag for better scroll performance
});
