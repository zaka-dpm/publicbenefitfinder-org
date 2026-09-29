(function () {
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
