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

  // --- Pronunciation: play the FIXED pre-generated clip (rendered from explicit
  // phonemes, so it's correct + identical for everyone). Fall back to the browser's
  // speech engine only if a clip happens to be missing. ---
  var synth = window.speechSynthesis;
  var VOWEL = { a: "ah", e: "eh", i: "ee", o: "oe", u: "oo" };
  var ONSET = { p: "p", t: "t", k: "k", f: "f", s: "s", h: "h",
                m: "m", n: "n", l: "l", w: "w", j: "y" };
  function faleniToSpeech(text) {
    return text.toLowerCase().replace(/[^a-z\s]/g, "").split(/\s+/)
      .filter(Boolean).map(function (word) {
        var syl = word.match(/[ptkfshmnlwj]?[aeiou]/g) || [];
        return syl.map(function (s) {
          var v = s.charAt(s.length - 1);
          var on = s.length > 1 ? (ONSET[s.charAt(0)] || "") : "";
          return on + VOWEL[v];
        }).join("");
      }).join(", ");
  }
  function speakTTS(text) {                       // fallback only
    if (!synth) return;
    var phon = faleniToSpeech(text);
    if (!phon) return;
    try {
      if (synth.speaking || synth.pending) synth.cancel();
      synth.resume();
      var u = new SpeechSynthesisUtterance(phon);
      u.lang = "en-US"; u.rate = 0.85;
      var vs = (synth.getVoices() || []).filter(function (v) { return /^en/i.test(v.lang); });
      var local = vs.filter(function (v) { return v.localService; });
      var voice = local[0] || vs[0];
      if (voice) u.voice = voice;
      synth.speak(u);
    } catch (e) { /* ignore */ }
  }
  function slugify(s) {
    return (s || "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
  }
  function playClip(slug) {                        // resolves when the clip finishes
    return new Promise(function (resolve, reject) {
      var a = new Audio("assets/audio/" + slug + ".mp3");
      a.addEventListener("ended", resolve);
      a.addEventListener("error", reject);
      a.play().catch(reject);
    });
  }
  function playWords(words, i) {                    // play each word's clip in sequence
    if (i >= words.length) return;
    playClip(slugify(words[i])).then(
      function () { setTimeout(function () { playWords(words, i + 1); }, 120); },
      function () { speakTTS(words.slice(i).join(" ")); }   // missing clip -> TTS the rest
    );
  }
  function playSay(text) {
    var words = (text || "").trim().split(/\s+/).filter(Boolean);
    if (!words.length) return;
    // Prefer the natural full-phrase clip; if it's missing, chain the word clips;
    // only if even those are absent do we fall back to the browser speech engine.
    playClip(slugify(text)).catch(function () {
      if (words.length > 1) playWords(words, 0);
      else speakTTS(text);
    });
  }
  document.addEventListener("click", function (e) {
    var btn = e.target && e.target.closest && e.target.closest("[data-say]");
    if (btn) { e.preventDefault(); playSay(btn.getAttribute("data-say")); }
  });
  // Keyboard activation for tap-to-hear words that aren't native buttons
  // (the <code>/<span> tokens get role="button" + tabindex="0").
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" && e.key !== " " && e.key !== "Spacebar") return;
    var el = e.target;
    if (!el || !el.getAttribute || el.getAttribute("role") !== "button") return;
    if (el.tagName === "BUTTON" || el.tagName === "A") return;   // those fire click natively
    var say = el.getAttribute("data-say");
    if (say) { e.preventDefault(); playSay(say); }
  });

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

  // --- Listening quiz: tap the play button, then choose the meaning ---
  document.addEventListener("click", function (e) {
    var opt = e.target && e.target.closest && e.target.closest(".quiz-opt");
    if (!opt) return;
    var q = opt.closest(".quiz-q");
    if (!q || q.classList.contains("done")) return;     // locked once answered correctly
    if (opt.getAttribute("data-correct") === "1") {
      opt.classList.add("is-correct");
      q.classList.add("done");
    } else {
      opt.classList.add("is-wrong");
      opt.setAttribute("disabled", "");                 // can't re-pick the same wrong one
    }
  });
  // Shuffle each question's options so the correct one isn't always first.
  (function () {
    var groups = document.querySelectorAll(".quiz-opts");
    for (var g = 0; g < groups.length; g++) {
      var box = groups[g];
      var kids = Array.prototype.slice.call(box.children);
      for (var i = kids.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var t = kids[i]; kids[i] = kids[j]; kids[j] = t;
      }
      kids.forEach(function (k) { box.appendChild(k); });
    }
  })();
})();
