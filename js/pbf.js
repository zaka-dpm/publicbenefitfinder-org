/* @ds-bundle: {"format":4,"namespace":"PublicBenefitFinder","components":[{"name":"Logo"},{"name":"SiteHeader"},{"name":"Button"},{"name":"Badge"},{"name":"Finder"},{"name":"CategoryIndex"},{"name":"ProgramResult"},{"name":"HowItWorks"},{"name":"Notice"},{"name":"SiteFooter"}]} */
(function () {
  "use strict";
  var ZIP = /^\d{5}$/;
  function setError(field, input, message) {
    var id = input.id + "-error";
    var existing = document.getElementById(id);
    if (!message) {
      field.classList.remove("pbf-field--error");
      input.removeAttribute("aria-invalid");
      if (existing) existing.remove();
      input.setAttribute("aria-describedby", input.id + "-help");
      return;
    }
    field.classList.add("pbf-field--error");
    input.setAttribute("aria-invalid", "true");
    input.setAttribute("aria-describedby", input.id + "-help " + id);
    if (!existing) {
      existing = document.createElement("p");
      existing.className = "pbf-error";
      existing.id = id;
      field.appendChild(existing);
    }
    existing.innerHTML = '<svg class="pbf-icon" viewBox="0 0 256 256" aria-hidden="true"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm-8-80V80a8,8,0,0,1,16,0v56a8,8,0,0,1-16,0Zm20,36a12,12,0,1,1-12-12A12,12,0,0,1,140,172Z"/></svg><span>Error: ' + message + "</span>";
  }
  /* Validates the ZIP field on submit and on blur once it has been touched. */
  function initFinder(root) {
    var form = (root || document).querySelector("[data-pbf-finder]");
    if (!form) return;
    var input = form.querySelector("input[name=zip]");
    var field = input.closest(".pbf-field");
    var touched = false;
    function check() {
      var v = input.value.trim();
      if (!v) return "Enter your ZIP code.";
      if (!ZIP.test(v)) return "Enter a 5-digit ZIP code, like 85004.";
      return "";
    }
    input.addEventListener("blur", function () { if (touched) setError(field, input, check()); });
    input.addEventListener("input", function () { touched = true; if (field.classList.contains("pbf-field--error")) setError(field, input, check()); });
    form.addEventListener("submit", function (e) {
      var msg = check();
      setError(field, input, msg);
      if (msg) { e.preventDefault(); input.focus(); }
    });
  }
  window.PublicBenefitFinder = { version: 1, initFinder: initFinder };
})();
