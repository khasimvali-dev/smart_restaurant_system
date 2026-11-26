(function () {
  const root = document.documentElement;
  const THEME_KEY = "srbas-theme";

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const toggle = document.getElementById("themeToggle");
    if (toggle) {
      const icon = toggle.querySelector("i");
      const label = toggle.querySelector("span");
      if (theme === "dark") {
        icon.className = "bi bi-sun";
        if (label) label.textContent = "Light mode";
      } else {
        icon.className = "bi bi-moon-stars";
        if (label) label.textContent = "Dark mode";
      }
    }
  }

  const saved = localStorage.getItem(THEME_KEY) || "light";
  applyTheme(saved);

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("themeToggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        const current = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        localStorage.setItem(THEME_KEY, current);
        applyTheme(current);
      });
    }

    const burger = document.getElementById("sidebarBurger");
    const sidebar = document.getElementById("sidebar");
    if (burger && sidebar) {
      burger.addEventListener("click", () => sidebar.classList.toggle("open"));
    }

    // Keyboard shortcuts (advanced feature #7)
    document.addEventListener("keydown", function (e) {
      if (e.altKey && e.key.toLowerCase() === "n") {
        window.location.href = "/billing/";
      }
      if (e.altKey && e.key.toLowerCase() === "d") {
        window.location.href = "/";
      }
      if (e.altKey && e.key.toLowerCase() === "s") {
        window.location.href = "/sales/";
      }
    });
  });
})();
