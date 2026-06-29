/* Faleni site — progressive enhancement. No dependencies. */
(function () {
  "use strict";

  // --- Mobile nav toggle ---
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // --- Dictionary search + family filter ---
  var search = document.getElementById("dict-search");
  if (search) {
    var rows = Array.prototype.slice.call(document.querySelectorAll("tr.dict-row"));
    var chips = Array.prototype.slice.call(document.querySelectorAll(".family-chip"));
    var countEl = document.getElementById("dict-count");
    var emptyEl = document.getElementById("dict-empty");
    var activeFamily = "all";
    var total = rows.length;

    function apply() {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i];
        var hay = r.getAttribute("data-search") || "";
        var fam = r.getAttribute("data-family") || "";
        var okText = q === "" || hay.indexOf(q) !== -1;
        var okFam = activeFamily === "all" || fam === activeFamily;
        var show = okText && okFam;
        r.style.display = show ? "" : "none";
        if (show) shown++;
      }
      if (countEl) {
        countEl.textContent = shown === total
          ? (total + " entries")
          : (shown + " of " + total + " entries");
      }
      if (emptyEl) emptyEl.style.display = shown === 0 ? "block" : "none";
    }

    var t;
    search.addEventListener("input", function () { clearTimeout(t); t = setTimeout(apply, 80); });
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.classList.remove("is-active"); });
        chip.classList.add("is-active");
        activeFamily = chip.getAttribute("data-family");
        apply();
      });
    });
    apply();
  }

  // --- Contribute: build a CSV line and a prefilled GitHub proposal link ---
  var form = document.getElementById("propose-form");
  if (form) {
    var repo = form.getAttribute("data-repo") || "";
    var repoOk = repo && repo.indexOf("your-username") === -1;
    var out = document.getElementById("propose-out");
    var link = document.getElementById("propose-link");
    if (link && !repoOk) {                       // never point the CTA at a placeholder repo
      link.removeAttribute("href");
      link.classList.add("is-disabled");
      link.setAttribute("aria-disabled", "true");
      link.title = "Maintainer: set the GitHub repo to enable this.";
    }
    function esc(s) { return (s || "").replace(/,/g, " "); }
    function update() {
      var word = (document.getElementById("p-word").value || "").trim().toLowerCase();
      var gloss = esc(document.getElementById("p-gloss").value.trim());
      var fam = document.getElementById("p-family").value;
      var line = word + ",root," + gloss + ",," + fam + ",";
      out.textContent = line;
      if (link && repoOk) {
        var title = encodeURIComponent("Propose word: " + word + " = " + gloss);
        var body = encodeURIComponent(
          "Proposed lexicon.csv line:\n\n    " + line +
          "\n\nDomain/onset family: " + fam +
          "\n\nChecklist:\n- [ ] ran `python3 tools/faleni.py check " + word + "`\n- [ ] legal shape, not taken, right family"
        );
        link.href = repo + "/issues/new?title=" + title + "&body=" + body;
      }
    }
    form.addEventListener("input", update);
    update();
  }
})();
