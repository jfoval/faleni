# Adding words to Faleni — the coinage protocol

This is the "system to keep adding words." Follow it and the language grows
without ever becoming irregular, ambiguous, or self‑contradictory.

The golden rule: **try to build the word before you invent one.** A language
that composes stays small and learnable; a language that hoards roots becomes
another English. Walk the layers in order and stop at the first that works.

---

## The decision ladder

```
Need a word for X?
│
├─ 1. Can I COMPOUND it from existing roots?      → do that.  (preferred)
│        "phone" = teku (tool) + fa (speak) = "teku fa"
│
├─ 2. Is it a regular DERIVATION (er/place/ness/opposite/tool)?
│        → use a semantic head.   "teacher" = pa (person) + fapi (teach)
│
├─ 3. Is it a basic, frequent, truly ATOMIC idea with no good build?
│        → coin a NEW ROOT in the right onset-family (rules below). Rare.
│
└─ 4. Is it a proper name or arbitrary technical term?
         → BORROW it: transliterate + mark with "ji".  "ji kolote" = Claude
```

Compound and derivation cover ~95% of real needs. New roots are for genuine
primitives only.

---

## 1. Compounds

- Order is **head first**: `A B` means "an A, of the B kind / related to B".
- Keep compounds to 2–3 roots.
- Write the parts with spaces.

| Want | Build | Faleni |
|---|---|---|
| pet | animal + house | `samu tu` |
| river | water + road | `sa tewi` |
| student | person + learn | `pa famu` |
| kitchen | place + (make + food) | `ti ke kema` |
| airplane | tool + fly | `teku kuwi` |

## 2. Derivation with semantic heads

These roots already exist; using them in head position is "derivation":

| Head | Pattern | Example → meaning |
|---|---|---|
| `pa` person | one who ___ | `pa komi` → buyer |
| `ti` place | place of ___ | `ti famu` → school |
| `teku` tool | device for ___ | `teku fano` → pen |
| `te` thing | thing that/for ___ | `te kopi` → toy |
| `niso` ‑ness | quality of ___ | `niso lefu` → strength |
| `noli` opposite | reverse of ___ | `noli kipa` → to end |

## 3. Coining a NEW ROOT (use sparingly)

Only for frequent, primitive ideas you genuinely can't build. Requirements:

1. **Right onset‑family.** Start the word with the consonant for its domain (see
   the table below) — this keeps the vocabulary navigable and is the whole point
   of the system.
2. **Legal shape:** `(C)V(CV)…` using only `a e i o u p t k f s h m n l w j`. In
   practice a new root is 2 syllables (`CVCV`). Reserve 1‑syllable forms for the
   top‑50 ideas — they are nearly all used already.
3. **Not taken, not too close:** must not collide; avoid one‑sound‑apart pairs
   inside the same family.
4. **Mnemonic if possible,** never at the cost of rules 1–3.

| Onset | Domain | | Onset | Domain |
|---|---|---|---|---|
| `p` | people & body | | `l` | qualities & color |
| `m` | mind & feeling | | `f` | speech & info |
| `s` | nature | | `n` | number, time, relation |
| `t` | things & places | | vowel | logic & connectives |
| `k` | actions | | | |

(`h`/`j` = grammar, `w` = pronouns, and the numerals are closed sets — don't coin
into them.)

Validate before you commit:

```sh
python3 tools/faleni.py check masu    # legal? taken? which family? too close?
python3 tools/faleni.py family        # the onset->domain legend + counts
python3 tools/faleni.py free          # which 1-syllable slots remain
```

## 4. Borrowing (proper names & arbitrary terms)

1. **Transliterate** to Faleni sounds: map each source sound to the nearest
   Faleni letter (`r`→`l`, `v`→`f`/`w`, `g`→`k`, `b`→`p`, `d`→`t`, `th`→`t`/`s`);
   break clusters and final consonants with a vowel (default `o`, or `i` after
   front sounds); drop anything Faleni can't represent.
2. **Mark it** with the name particle **`ji`** so it's never parsed as a
   compound: `ji kolote` (Claude), `ji amelika` (America).
3. **Register** it (next section).

---

## Registering a word (so it's permanent and collision‑free)

Every accepted word goes into [lexicon.csv](lexicon.csv), one row:

```
word,type,gloss,decomp,domain,notes
```

- **word** — the Faleni form (no spaces for a root; spaces allowed for a recorded
  compound).
- **type** — `particle` | `pronoun` | `number` | `question` | `root` |
  `compound` | `name`.
- **gloss** — English meaning(s), separated by `/`. **No commas** (CSV).
- **decomp** — how it's built, e.g. `pa+fapi`. Blank for primitives.
- **domain** — the onset‑family: `people`, `mind`, `nature`, `thing`, `action`,
  `quality`, `color`, `speech`, `time`, `logic` (or `grammar`/`pronoun`/`number`).
- **notes** — anything useful. No commas.

Then re‑run the validator:

```sh
python3 tools/faleni.py        # should report 0 errors, 0 collisions
```

That loop — **build → check → register → validate** — is the whole system. Run
it a thousand times and Faleni stays exactly as regular as it is today.

---

## A worked example

> I want to say **"library."**

1. Compound? A library is a *house of books*: `tu` (house) + `fila` (book) →
   **`tu fila`**.
2. The parts exist and it reads cleanly — done. A transparent compound needs no
   registry row, but if it's common in your texts, record it:
   `tu fila,compound,library,tu+fila,thing,house of books`
3. `python3 tools/faleni.py` → 0 errors. No new root needed.

> I want a new root for **"snow"** (a basic nature thing, no good compound).

1. Nature ⇒ onset `s`. Try `sumi`… `python3 tools/faleni.py check sumi`.
2. If taken or too close, try `sefo`, `siso`, … until one is clean.
3. Register: `siso,root,snow,,nature,` → validate → done.
