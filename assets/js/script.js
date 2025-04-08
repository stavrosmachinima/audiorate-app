document.addEventListener("DOMContentLoaded", function () {
  // Find all rating containers
  const ratingContainers = document.querySelectorAll(".rating-container");
  const starCount = 5; // Total number of stars
  const progressBar = document.querySelector(".progress-bar");
  const ratingInputs = document.querySelectorAll("input[id^='rating-value-']");

  function updateProgressBar() {
    if (!progressBar) return;

    const completedRatings = Array.from(ratingInputs).filter(
      (input) => parseFloat(input.value) > 0
    ).length;
    const totalRatings = ratingInputs.length;
    const progressPercentage =
      completedRatings >= totalRatings
        ? 100
        : Math.round((completedRatings / totalRatings) * 100);
    console.log(
      `Completed Ratings: ${completedRatings}, Total Ratings: ${totalRatings}, Progress: ${progressPercentage}%`
    );
    progressBar.style.width = `${progressPercentage}%`;
    progressBar.setAttribute("aria-valuenow", progressPercentage);
    progressBar.textContent = `${progressPercentage}% completed`;
  }

  ratingContainers.forEach((container) => {
    const rateitRange = container.querySelector(".rateit-range");
    const rateitSelected = container.querySelector(".rateit-selected");
    const rateitHover = container.querySelector(".rateit-hover");
    const hiddenInput = container.querySelector('input[type="hidden"]');

    function getStarWidth() {
      return rateitRange.offsetWidth / starCount;
    }

    let starWidthPx = getStarWidth();

    function getStarValueFromPosition(position) {
      const halfStarWidth = starWidthPx / 2;
      let starValue = Math.ceil(position / halfStarWidth) / 2;
      return Math.max(0.5, Math.min(starCount, starValue));
    }

    function updateRatingDisplay(element, starValue, showElement = true) {
      starWidthPx = getStarWidth();
      element.style.width = `${starValue * starWidthPx}px`;
      element.style.display = showElement ? "block" : "none";
    }

    rateitRange.addEventListener("mousemove", function (e) {
      const position = e.clientX - this.getBoundingClientRect().left;
      const starValue = getStarValueFromPosition(position);
      updateRatingDisplay(rateitHover, starValue);
    });

    rateitRange.addEventListener("mouseleave", function () {
      rateitHover.style.display = "none";
    });

    rateitRange.addEventListener("click", function (e) {
      const position = e.clientX - this.getBoundingClientRect().left;
      const starValue = getStarValueFromPosition(position);
      updateRatingDisplay(rateitSelected, starValue);
      hiddenInput.value = starValue;
      this.setAttribute("aria-valuenow", starValue * 2);

      updateProgressBar();
    });

    if (hiddenInput.value && parseFloat(hiddenInput.value) > 0) {
      const starValue = parseFloat(hiddenInput.value);
      updateRatingDisplay(rateitSelected, starValue);

      rateitRange.setAttribute("aria-valuenow", starValue * 2);
    }
  });

  window.addEventListener(
    "resize",
    function () {
      ratingContainers.forEach((container) => {
        const rateitRange = container.querySelector(".rateit-range");
        const rateitSelected = container.querySelector(".rateit-selected");
        const hiddenInput = container.querySelector('input[type="hidden"]');
        const starValue = parseFloat(hiddenInput.value) || 0;
        const starWidthPx = rateitRange.offsetWidth / starCount;
        rateitSelected.style.width = `${starValue * starWidthPx}px`;
      });
    },
    { passive: true }
  );
  updateProgressBar();
});
