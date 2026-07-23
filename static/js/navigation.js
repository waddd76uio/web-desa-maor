(function () {
  "use strict";

  function initializeNavigation() {
    const navToggle = document.querySelector(".nav-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (!navToggle || !navLinks) {
      console.warn("Navbar mobile tidak ditemukan.");
      return;
    }

    function closeNavigation() {
      navLinks.classList.remove("is-open");
      navToggle.classList.remove("is-open");

      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "Buka menu navigasi");
    }

    function openNavigation() {
      navLinks.classList.add("is-open");
      navToggle.classList.add("is-open");

      navToggle.setAttribute("aria-expanded", "true");
      navToggle.setAttribute("aria-label", "Tutup menu navigasi");
    }

    navToggle.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();

      const menuIsOpen = navLinks.classList.contains("is-open");

      if (menuIsOpen) {
        closeNavigation();
      } else {
        openNavigation();
      }
    });

    navLinks.addEventListener("click", function (event) {
      event.stopPropagation();
    });

    navLinks.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeNavigation);
    });

    document.addEventListener("click", function (event) {
      if (
        !navLinks.contains(event.target) &&
        !navToggle.contains(event.target)
      ) {
        closeNavigation();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeNavigation();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 1100) {
        closeNavigation();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      initializeNavigation,
      { once: true }
    );
  } else {
    initializeNavigation();
  }
})();