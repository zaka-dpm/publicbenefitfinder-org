(function () {
  "use strict";
  var root = document.querySelector("[data-benefit-wizard]");
  if (!root) return;
  var catalog, index = 0;
  var params = new URLSearchParams(location.search);
  var answers = { state: params.get("state") || "", zip: params.get("zip") || "", need: params.get("need") || "", urgency: "", household: [], income: "", notice: "" };
  var needs = [["food", "Food and groceries"], ["housing", "Housing or rent"], ["utilities", "Utility bills"], ["health", "Health coverage"], ["cash", "Cash and income support"], ["childcare", "Child care"]];
  function escape(value) { return String(value).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function steps() {
    var list = [{ id: "state", title: "Where do you live?", hint: "Choose your state so we can show its programs. Your ZIP code is optional.", type: "location" }, { id: "need", title: "What do you need help with?", hint: "Choose the kind of help you want to explore first.", options: needs }];
    if (answers.need === "housing" || answers.need === "utilities") list.push({ id: "notice", title: answers.need === "housing" ? "Have you received an eviction or late-rent notice?" : "Have you received a shutoff notice?", options: [["yes", "Yes"], ["no", "No"], ["skip", "Prefer not to say"]] });
    list.push({ id: "urgency", title: "How soon do you need help?", options: [["today", "Today"], ["soon", "Within the next week or two"], ["planning", "I’m planning ahead"]] });
    list.push({ id: "household", title: "Does any of this describe your household?", hint: "Select all that apply. This helps us order the resources.", type: "multi", options: [["children", "Children under 18"], ["senior", "Someone age 60 or older"], ["disabled", "Someone with a disability"], ["veteran", "A veteran or active service member"], ["none", "None of these"], ["skip", "Prefer not to say"]] });
    list.push({ id: "income", title: "What is your household’s monthly income?", hint: "Optional. We’ll explain what information to prepare; this does not calculate eligibility.", options: [["lt1000", "Under $1,000"], ["1000-2500", "$1,000–$2,500"], ["2500-4000", "$2,500–$4,000"], ["gt4000", "Over $4,000"], ["skip", "Prefer not to say"]] });
    return list;
  }
  function focusTitle() { var title = root.querySelector("[data-step-title]"); if (title) title.focus(); }
  function render(focus) {
    var list = steps(), step = list[index], percent = Math.round(index / list.length * 100);
    var fields;
    if (step.type === "location") {
      fields = '<label class="pbf-label" for="finder-state">Your state</label><select class="pbf-input" id="finder-state" name="state" required><option value="">Choose your state</option>' + catalog.states.map(function (s) { return '<option value="' + s.slug + '"' + (answers.state === s.slug ? ' selected' : '') + '>' + escape(s.name) + '</option>'; }).join("") + '</select><label class="pbf-label" for="finder-zip">ZIP code (optional)</label><input class="pbf-input pbf-input--zip" id="finder-zip" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" value="' + escape(answers.zip) + '"><p class="pbf-small pbf-muted">Results use your selected state. The ZIP code is not used to locate county or city services.</p>';
    } else {
      fields = '<fieldset class="pbf-fieldset"><legend class="pbf-visually-hidden">' + escape(step.title) + '</legend><div class="site-wizard-options">' + step.options.map(function (option) {
        var checked = step.type === "multi" ? answers.household.indexOf(option[0]) !== -1 : answers[step.id] === option[0];
        return '<label class="site-wizard-option"><input type="' + (step.type === "multi" ? 'checkbox' : 'radio') + '" name="' + step.id + '" value="' + option[0] + '"' + (checked ? ' checked' : '') + '><span>' + escape(option[1]) + '</span></label>';
      }).join("") + '</div></fieldset>';
    }
    root.innerHTML = '<div class="site-wizard-stepbar"><span>Step ' + (index + 1) + ' of ' + list.length + '</span><span>' + percent + '%</span></div><progress class="site-wizard-progress" value="' + index + '" max="' + list.length + '" aria-label="Questionnaire progress"></progress><h2 class="pbf-h2" tabindex="-1" data-step-title>' + step.title + '</h2>' + (step.hint ? '<p class="pbf-muted">' + step.hint + '</p>' : '') + '<form novalidate>' + fields + '<p class="pbf-error" data-error role="alert"></p><div class="site-wizard-actions">' + (index ? '<button class="pbf-btn pbf-btn--secondary" type="button" data-back>Back</button>' : '') + '<button class="pbf-btn pbf-btn--primary" type="submit">' + (index === list.length - 1 ? 'Show programs' : 'Continue') + '</button></div></form><p class="pbf-small pbf-muted">Your answers stay in this page and clear when you leave or reload. No account is needed.</p>';
    var form = root.querySelector("form");
    function save() {
      var data = new FormData(form);
      if (step.type === "location") { answers.state = data.get("state"); answers.zip = String(data.get("zip")).trim(); }
      else if (step.type === "multi") answers.household = data.getAll("household");
      else { var value = data.get(step.id); if (step.id === "need" && value !== answers.need) answers.notice = ""; answers[step.id] = value || ""; }
    }
    form.addEventListener("change", function (event) {
      if (step.type !== "multi") return;
      var chosen = event.target;
      if (chosen.checked) form.querySelectorAll("input").forEach(function (input) {
        if (input !== chosen && (["none", "skip"].indexOf(chosen.value) !== -1 || ["none", "skip"].indexOf(input.value) !== -1)) input.checked = false;
      });
    });
    form.addEventListener("submit", function (event) {
      event.preventDefault(); save();
      var error = "";
      if (step.type === "location") {
        if (!catalog.states.some(function (s) { return s.slug === answers.state; })) error = "Choose your state.";
        else if (answers.zip && !/^\d{5}$/.test(answers.zip)) error = "Enter a 5-digit ZIP code or leave it blank.";
      } else if (step.type === "multi" ? !answers.household.length : !answers[step.id]) error = "Choose an option to continue.";
      root.querySelector("[data-error]").textContent = error;
      if (error) return;
      if (index < steps().length - 1) { index++; render(true); } else results();
    });
    var back = root.querySelector("[data-back]");
    if (back) back.addEventListener("click", function () { save(); index--; render(true); });
    if (focus) focusTitle();
  }
  function results() {
    var state = catalog.states.find(function (s) { return s.slug === answers.state; });
    var programs = state.programs.filter(function (p) { return p.category === answers.need; });
    programs.sort(function (a, b) {
      function score(p) { return p.tags.reduce(function (sum, tag) { return sum + (answers.household.indexOf(tag) !== -1 ? 1 : 0); }, 0); }
      return score(b) - score(a);
    });
    var urgent = answers.urgency === "today" || answers.notice === "yes";
    var urgentText = answers.need === "food" ? 'Ask about emergency food distribution and expedited SNAP processing.' : answers.need === "housing" ? 'Tell the local agency about any eviction notice and its deadline.' : answers.need === "utilities" ? 'Tell the agency about any shutoff notice and contact your utility about available payment arrangements.' : 'Tell the agency that your need is urgent.';
    root.innerHTML = '<h2 class="pbf-h2" tabindex="-1" data-step-title>Programs to explore in ' + escape(state.name) + '</h2><p>These starting points match your state and type of help. Household answers order the list; agencies determine eligibility.</p>' + (urgent ? '<div class="site-wizard-urgent"><h3 class="pbf-h3">Need help now?</h3><p>' + urgentText + ' Call <a href="tel:211">211</a> for local assistance. For an emergency, call 911.</p></div>' : '') + (answers.income && answers.income !== "skip" ? '<p class="pbf-small pbf-muted">When applying, prepare income records for everyone applying in your household. A rough income range alone cannot determine eligibility or benefit amounts.</p>' : '') + (programs.length ? '<ul class="pbf-results">' + programs.map(function (p) {
      var link = p.guide || '/help/' + state.slug + '/#' + p.slug;
      return '<li class="pbf-program"><div class="pbf-program__main"><h3 class="pbf-h3"><a href="' + link + '">' + escape(p.title) + '</a></h3><p>' + escape(p.description) + '</p></div><div class="pbf-program__actions"><a class="pbf-link" href="' + link + '">' + (p.guide ? 'Read the guide' : 'View in the state directory') + '</a></div></li>';
    }).join("") + '</ul>' : '<p>Our current directory has no entries for that type of help in ' + escape(state.name) + '. Other assistance may be available; contact 211 or browse your state’s resources.</p>') + '<div class="site-wizard-actions"><a class="pbf-btn pbf-btn--primary" href="/help/' + state.slug + '/">All ' + escape(state.name) + ' programs</a><button class="pbf-btn pbf-btn--secondary" type="button" data-edit>Edit answers</button><button class="pbf-btn pbf-btn--secondary" type="button" data-restart>Start again</button></div>';
    root.querySelector("[data-edit]").addEventListener("click", function () { index = 0; render(true); });
    root.querySelector("[data-restart]").addEventListener("click", function () { answers = { state: "", zip: "", need: "", urgency: "", household: [], income: "", notice: "" }; index = 0; render(true); });
    focusTitle();
  }
  fetch("/data/finder-programs.json").then(function (response) { if (!response.ok) throw new Error("Catalog unavailable"); return response.json(); }).then(function (data) {
    catalog = data;
    if (!catalog.states.some(function (s) { return s.slug === answers.state; })) answers.state = "";
    if (!needs.some(function (n) { return n[0] === answers.need; })) answers.need = "";
    render(false);
  }).catch(function () { root.innerHTML = '<p role="alert">The finder could not load. You can still <a href="/help/">browse programs by state</a>.</p>'; });
})();
