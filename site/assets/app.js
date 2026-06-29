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

  // --- Pronunciation: speak any Faleni word via the browser's speech engine ---
  // Faleni is perfectly phonemic, so we respell it into English-phonetic syllables
  // (pure vowels, j -> y) and let the synthesizer read it. Stress is first-syllable.
  var synth = window.speechSynthesis;
  if (!synth) {
    document.documentElement.classList.add("no-speech");   // CSS hides the buttons
  } else {
    var VOWEL = { a: "ah", e: "eh", i: "ee", o: "oh", u: "oo" };
    var ONSET = { p: "p", t: "t", k: "k", f: "f", s: "s", h: "h",
                  m: "m", n: "n", l: "l", w: "w", j: "y" };
    var faleniToSpeech = function (text) {
      return text.toLowerCase().replace(/[^a-z\s]/g, "").split(/\s+/)
        .filter(Boolean).map(function (word) {
          var syl = word.match(/[ptkfshmnlwj]?[aeiou]/g) || [];
          return syl.map(function (s) {
            var v = s.charAt(s.length - 1);
            var on = s.length > 1 ? (ONSET[s.charAt(0)] || "") : "";
            return on + VOWEL[v];
          }).join("-");
        }).join(", ");
    };
    // Voices can populate asynchronously; prime them so getVoices() isn't empty.
    var primeVoices = function () { try { synth.getVoices(); } catch (e) {} };
    primeVoices();
    if ("onvoiceschanged" in synth) synth.onvoiceschanged = primeVoices;
    var pickVoice = function () {
      var vs = synth.getVoices() || [];
      var en = vs.filter(function (v) { return /^en/i.test(v.lang); });
      var local = en.filter(function (v) { return v.localService; });
      return local[0] || en[0] || null;          // prefer an on-device English voice
    };
    var speak = function (text) {
      var phon = faleniToSpeech(text);
      if (!phon) return;
      try {
        if (synth.speaking || synth.pending) synth.cancel();
        synth.resume();                           // Chrome silently pauses when idle
        var u = new SpeechSynthesisUtterance(phon);
        u.lang = "en-US";
        u.rate = 0.85;
        var v = pickVoice();
        if (v) u.voice = v;
        synth.speak(u);
      } catch (e) { /* ignore */ }
    };
    document.addEventListener("click", function (e) {
      var btn = e.target && e.target.closest && e.target.closest("[data-say]");
      if (btn) { e.preventDefault(); speak(btn.getAttribute("data-say")); }
    });
  }

  // --- Lesson cards: reveal the meaning after you've heard & said the word ---
  document.addEventListener("click", function (e) {
    var r = e.target && e.target.closest && e.target.closest(".reveal");
    if (!r) return;
    var card = r.closest(".say-card");
    var m = card && card.querySelector(".meaning");
    if (m) {
      var show = m.hidden;
      m.hidden = !show;
      r.textContent = show ? "hide meaning" : "show meaning";
      r.setAttribute("aria-expanded", show ? "true" : "false");
    }
  });
})();
