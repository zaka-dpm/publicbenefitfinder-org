(function () {
  var guideSearch = document.querySelector("[data-guide-search]");
  if (guideSearch) {
    var searchInput = guideSearch.querySelector("input[type=search]");
    var groups = document.querySelectorAll(".site-group");
    var empty = document.createElement("p");
    empty.textContent = "No matching program types. Try another search or browse by state.";
    empty.setAttribute("role", "status");
    empty.hidden = true;
    document.querySelector(".site-groups").after(empty);
    function filterGuides() {
      var query = searchInput.value.trim().toLowerCase(), total = 0;
      groups.forEach(function (group) {
        var visible = 0;
        group.querySelectorAll("ul li").forEach(function (item) {
          var matches = !query || item.textContent.toLowerCase().indexOf(query) !== -1 || group.querySelector("h2").textContent.toLowerCase().indexOf(query) !== -1;
          item.hidden = !matches;
          if (matches) visible++;
        });
        group.hidden = !visible; total += visible;
      });
      empty.hidden = total > 0;
    }
    searchInput.value = new URLSearchParams(location.search).get("q") || "";
    guideSearch.addEventListener("submit", function (event) { event.preventDefault(); filterGuides(); });
    searchInput.addEventListener("input", filterGuides);
    filterGuides();
  }
  var statePicker = document.querySelector("[data-state-picker]");
  if (statePicker) statePicker.addEventListener("submit", function (event) {
    event.preventDefault();
    var select = statePicker.querySelector("select");
    if (!select.value) { select.setCustomValidity("Choose your state."); select.reportValidity(); return; }
    window.location.assign("/help/" + encodeURIComponent(select.value) + "/");
  });
  if (statePicker) statePicker.querySelector("select").addEventListener("change", function () { this.setCustomValidity(""); });
  if (window.PublicBenefitFinder) PublicBenefitFinder.initFinder(document);
  var btn = document.querySelector("[data-menu-toggle]");
  var menu = document.getElementById("mobile-menu");
  if (!btn || !menu) return;
  btn.addEventListener("click", function () {
    var open = btn.getAttribute("aria-expanded") !== "true";
    btn.setAttribute("aria-expanded", String(open));
    menu.setAttribute("data-open", String(open));
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") {
      btn.setAttribute("aria-expanded", "false"); menu.setAttribute("data-open", "false"); btn.focus();
    }
  });
})();
