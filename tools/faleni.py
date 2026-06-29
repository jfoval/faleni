#!/usr/bin/env python3
"""faleni.py - validator and helper for the Faleni language.

Usage:
    python3 tools/faleni.py            Validate the whole lexicon and print stats.
    python3 tools/faleni.py free       List the unused 1-syllable forms (scarce slots).
    python3 tools/faleni.py family     Show the onset->domain legend and per-family counts.
    python3 tools/faleni.py check WORD  Check a candidate: legal? taken? right family?
    python3 tools/faleni.py suggest P 40  Emit 40 fresh 2-syllable forms for a family
                                          (consonant onset, or V for vowel-initial).

The lexicon lives in ../lexicon.csv relative to this script.
No third-party dependencies; Python 3.6+.
"""

import csv
import os
import re
import sys
from collections import Counter, defaultdict

ONSET = "ptkfshmnlwj"        # the 11 consonants
VOWEL = "aeiou"              # the 5 vowels
SYLLABLE = "[%s]?[%s]" % (ONSET, VOWEL)
LEGAL = re.compile(r"^(?:%s)+$" % SYLLABLE)

# Onset -> semantic family for the OPEN (content) vocabulary.
# Closed sets (grammar, pronouns, numerals) sit outside this scheme.
FAMILY = {
    "p": "people & body",
    "m": "mind & feeling",
    "s": "nature",
    "t": "things & places",
    "k": "actions",
    "l": "qualities & color",
    "f": "speech & info",
    "n": "number, time & relation",
    "": "logic & quantifier (vowel-initial)",
}
GRAMMAR_ONSETS = set("hj")   # grammar particles & question words
PRONOUN_ONSET = "w"          # pronouns & deictics

HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON = os.path.normpath(os.path.join(HERE, "..", "lexicon.csv"))


def syllables(word):
    return re.findall(SYLLABLE, word)


def onset(word):
    """First consonant of a word, or '' if it is vowel-initial."""
    return word[0] if word and word[0] in ONSET else ""


def load():
    with open(LEXICON, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_legal(word):
    return bool(LEGAL.match(word))


def all_one_syllable_forms():
    forms = ["" + v for v in VOWEL]                 # bare vowels
    forms += [c + v for c in ONSET for v in VOWEL]  # CV
    return forms


# --- commands ---------------------------------------------------------------

def cmd_validate():
    rows = load()
    errors = []
    seen = {}
    for row in rows:
        word = (row.get("word") or "").strip()
        for part in word.split():
            if not is_legal(part):
                errors.append("ILLEGAL   %-10s (uses a letter or shape Faleni forbids)" % word)
                break
        if word in seen:
            errors.append("COLLISION %-10s (already means: %s)" % (word, seen[word]))
        else:
            seen[word] = row.get("gloss", "")

    total = len(rows)
    by_type = Counter((r.get("type") or "?").strip() for r in rows)
    single = [r["word"] for r in rows
              if " " not in r["word"] and len(syllables(r["word"])) == 1]
    length_hist = Counter(len(syllables(r["word"])) for r in rows if " " not in r["word"])

    print("Faleni lexicon: %s" % LEXICON)
    print("-" * 64)
    print("entries:            %d" % total)
    print("by type:            %s" % ", ".join("%s=%d" % kv for kv in sorted(by_type.items())))
    print("syllable lengths:   %s" % ", ".join("%d-syl=%d" % kv for kv in sorted(length_hist.items())))
    print("1-syllable forms:   %d used of %d (%d free)"
          % (len(single), len(all_one_syllable_forms()),
             len(all_one_syllable_forms()) - len(single)))
    print("-" * 64)
    if errors:
        print("PROBLEMS (%d):" % len(errors))
        for e in errors:
            print("  " + e)
        return 1
    print("OK - 0 illegal forms, 0 collisions.")
    return 0


def cmd_free():
    rows = load()
    used = set(r["word"] for r in rows
               if " " not in r["word"] and len(syllables(r["word"])) == 1)
    free = [f for f in all_one_syllable_forms() if f not in used]
    print("Free 1-syllable forms (%d of %d). Reserve these for the most frequent"
          % (len(free), len(all_one_syllable_forms())))
    print("ideas only; ordinary new words take 2 syllables.\n")
    for i in range(0, len(free), 11):
        print("  " + "  ".join("%-3s" % f for f in free[i:i + 11]))
    return 0


def cmd_family():
    rows = load()
    counts = defaultdict(int)
    for r in rows:
        if r.get("type") == "root":
            counts[onset(r["word"])] += 1
    print("Onset -> domain. Start a NEW content word with the right onset:")
    print("-" * 64)
    for o in "pmstklfn":
        print("  %s-   %-26s  (%d roots)" % (o, FAMILY[o], counts[o]))
    print("  V-   %-26s  (%d roots)" % (FAMILY[""], counts[""]))
    print("-" * 64)
    print("  h-, j-  grammar particles & question words (closed set)")
    print("  w-      pronouns & deictics (closed set)")
    print("  numerals so..ku, na/to/fu (closed set)")
    return 0


def cmd_check(word):
    word = word.strip().lower()
    print("checking: %s" % word)
    if not is_legal(word):
        print("  ILLEGAL: uses sounds or shapes Faleni doesn't allow.")
        print("  Legal letters: %s %s ; every syllable is (consonant)+vowel." % (VOWEL, ONSET))
        return 1
    print("  legal shape: yes  (%s)" % "-".join(syllables(word)))
    o = onset(word)
    if o in FAMILY:
        print("  family:      %s-  ->  %s" % (o or "V", FAMILY[o]))
    elif o in GRAMMAR_ONSETS:
        print("  family:      %s-  ->  grammar (closed set)" % o)
    elif o == PRONOUN_ONSET:
        print("  family:      w-  ->  pronoun/deictic (closed set)")
    rows = load()
    taken = [r for r in rows if r["word"] == word]
    if taken:
        print("  TAKEN: already means '%s' (%s)." % (taken[0].get("gloss", "?"), taken[0].get("type", "?")))
        return 1
    print("  taken: no")
    near = []
    for r in rows:
        w = r["word"]
        if " " in w or len(w) != len(word) or w == word:
            continue
        if sum(1 for x, y in zip(w, word) if x != y) == 1:
            near.append("%s (%s)" % (w, r.get("gloss", "?")))
    if near:
        print("  note: close by ear to %s - usable, but keep it distinct." % ", ".join(near))
    else:
        print("  no close neighbors.")
    print("  --> available. Register it in lexicon.csv if you adopt it.")
    return 0


def cmd_suggest(onset_arg, n):
    onset = "" if onset_arg.upper() == "V" else onset_arg.lower()
    if onset and onset not in ONSET:
        print("unknown onset '%s' (use a consonant from %s, or V)" % (onset_arg, ONSET))
        return 2
    rows = load()
    taken = [r["word"] for r in rows if " " not in r["word"]]
    taken_set = set(taken)

    def hamming1(a, b):
        return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1

    cands = [onset + v1 + c + v2 for v1 in VOWEL for c in ONSET for v2 in VOWEL]
    emitted = []
    for cand in cands:
        if cand in taken_set:
            continue
        if any(hamming1(cand, t) for t in taken):       # 1 sound from an existing word
            continue
        emitted.append(cand)
        if len(emitted) >= n:
            break
    label = (onset + "-") if onset else "V-"
    print("%d fresh %s forms (legal, untaken, not a near-homophone of any existing word):"
          % (len(emitted), label))
    for i in range(0, len(emitted), 10):
        print("  " + " ".join(emitted[i:i + 10]))
    return 0


def main(argv):
    if len(argv) <= 1:
        return cmd_validate()
    cmd = argv[1]
    if cmd == "free":
        return cmd_free()
    if cmd == "family":
        return cmd_family()
    if cmd == "check" and len(argv) >= 3:
        return cmd_check(argv[2])
    if cmd == "suggest" and len(argv) >= 3:
        n = int(argv[3]) if len(argv) >= 4 else 40
        return cmd_suggest(argv[2], n)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
