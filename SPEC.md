# Faleni — Language Specification (v0.3)

This document fully defines Faleni. If something isn't here, it follows from the
rules here — there are no exceptions hiding elsewhere.

---

## 1. Design goals (and the trade‑offs we chose)

The brief: *the most optimal and efficient language, easy to learn, easy to
apply, with no rules that don't make sense, a system so there's a word for
everything — and completely original.*

"Optimal", "easy", and "original" pull against each other, so we made the
choices explicit:

| Pressure | Choice | Why |
|---|---|---|
| Compression vs. clarity | Favor clarity | A maximally compressed code is fragile when misheard. We keep tuned redundancy. |
| Brevity vs. learnability | Frequency‑weighted brevity | Short forms only for common words; everything else stays regular. |
| Precision vs. simplicity | Simple core, precise on demand | Tiny grammar; precision comes from *adding words*, not grammar rules. |
| Original vs. familiar | **Fully original (a priori)** | No root is borrowed from any language. To keep invented roots learnable, the **onset encodes the domain** (§3). |

The non‑negotiables: **no irregularities, no silent rules, one sound per letter,
every word invariant in shape, an open‑ended but collision‑free way to coin
words, and nothing borrowed from an existing language.**

---

## 2. Sounds and the alphabet

Faleni uses 16 Latin letters, each with exactly one sound. No digraphs, no silent
letters, no capitals required.

### Vowels (5)
`a e i o u` — as in *father, bet, machine, more, flute*. Length and pitch never
change meaning.

### Consonants (11)
`p t k f s h m n l w j`

- `j` = English **y** (as in *yes*). `ju` is pronounced "you".
- **Accent tolerance:** voicing is not meaningful, so `p≈b`, `t≈d`, `k≈g`,
  `f≈v`, `s≈z` are all accepted pronunciations of the same letters. A speaker
  who voices a stop is still understood. This lets speakers of many native
  languages be understood without retraining their mouths.

### Left out on purpose
No **r** (varies wildly; clashes with `l`); no **th**, no tones, no vowel‑length
or stress contrasts; no voiced/voiceless *pairs* competing for meaning. That
gives 11 × 5 = 55 simple, well‑spaced syllables.

---

## 3. The onset‑family architecture (Faleni's signature feature)

Because every root is invented, we gave the vocabulary a backbone: **the first
sound of a content word marks its meaning‑domain.**

| Onset | Domain | Examples |
|---|---|---|
| `p` | people & body | `pa` person, `pi` man, `pama` mother, `pika` head |
| `m` | mind, feeling, perception | `ma` know, `me` want, `mi` see, `masu` happy |
| `s` | nature & substance | `sa` water, `se` fire, `su` sun, `sena` moon |
| `t` | made things & places | `te` thing, `tu` house, `tuna` city, `teku` tool |
| `k` | actions & motion | `ka` go, `ke` make, `ko` give, `kema` eat |
| `l` | qualities & color | `la` good, `le` big, `li` small, `lasa` red |
| `f` | speech & information | `fa` speak, `fe` word, `fi` read, `fila` book |
| `n` | number, time, relation | `ni` amount, `no` time, `nita` day, `noli` opposite |
| vowel | logic & connectives | `a` all, `u` very, `isa` if, `uka` because |

Closed sets sit **outside** this scheme (they're learned once as a group):

- `h` and `j` → **grammar** particles and question words (`ha` is, `he` not,
  `jo` plural, `jeta` what…)
- `w` → **pronouns and deictics** (`wa` I, `we` you, `wi` they, `wo` this)
- **numerals** → `so ta ne ki fo pe lu si mo ku` (0–9) and `na to fu` (10/100/1000)

**Why only the first consonant?** The 1600s "philosophical languages" (Wilkins)
encoded a word's full taxonomy into its letters, so *salmon* and *trout* differed
by one sound and were impossible to tell apart. We took the lesson: fix only the
broad domain (one consonant), and let the rest of the word vary freely for
distinctness. The onset is a **memory hook and a coinage recipe — never a rule
you apply while speaking.**

---

## 4. Word shape, stress, and self‑segregation

- **Syllable = (C)V.** Optional consonant + vowel. The only syllable type. No
  clusters, no final consonants.
- A **word** is one or more syllables: `wa`, `tuna`, `jeta`, `faleni`.
- **Stress is always on the first syllable.** Never written, never contrastive —
  it just marks where each word begins, so speech is **self‑segregating**.

**Word length tracks frequency** (Zipf's law of abbreviation):

| Tier | Length | Used for |
|---|---|---|
| Particles + ~60 most common ideas | 1 syllable (`CV`) | `wa`, `ha`, `ka`, `la` |
| Common vocabulary | 2 syllables (`CVCV`) | `tuna`, `peni`, `kema` |
| Compounds, technical, borrowed | 2+ syllables | `teku fa`, `ji amelika` |

---

## 5. The whole grammar, in 10 rules

1. **Read it as written.** One letter, one sound. `j` = "y". Stress the first
   syllable.
2. **Sentence = `Subject  ha  Predicate`.** The word **`ha`** ("is/does") marks
   where the subject ends and the predicate begins. `wa ha fa` = "I speak."
3. **Head first, then its stuff.** Verb before object: `wa ha mu we` = "I love
   you." This one ordering rule is used everywhere (rule 4).
4. **Modifiers follow what they modify.** Adjective after noun, adverb after
   verb, number after noun, owner after the owned. `tu le` = "big house";
   `kali liwa` = "walk fast"; `tu wa` = "my house".
5. **Words never change shape.** No endings, ever. `kema` is *eat / ate / will
   eat / eating*.
6. **Roots have no fixed part of speech.** `fa` = *speech* (noun), *to speak*
   (verb), *verbal* (modifier) depending on slot.
7. **Negate with `he`,** right before what you deny. `wa ha he fa` = "I don't
   speak."
8. **Ask yes/no with `ho`** at the end. Ask everything else with a **`je‑`
   word** (`jeta` what, `jepi` who, `jewa` where, `jeni` when, `jesa` why,
   `jefe` how, `jenu` how‑many), placed where the answer would go.
   `we ha ka jewa?` = "Where are you going?"
9. **Join with `hi` (and) / `hu` (or).** `wa hi we` = "you and I".
10. **Make new words by describing them, head first** (§7). That's the whole
    vocabulary system.

There is no rule 11.

---

## 6. Pronouns, plural, time

**Pronouns** (one set, no gendered or object forms — all start `w`):

| Faleni | Meaning |
|---|---|
| `wa` | I / me / my |
| `we` | you / your |
| `wi` | he / she / it / they / their |
| `wo` | this / here |
| `wu` | that / there |

**Plural** is the word **`jo`** ("many") after the noun: `tu jo` = houses,
`wa jo` = we, `wi jo` = they. Possession needs no extra word — the owner
follows: `tu wa` = "my house" (optional `ja` for clarity: `tu ja wa`).

**Tense is optional.** Faleni is tenseless by default; context carries time. When
needed, add a time word — `napo` (past), `nima` (now), `nase` (future):

- `wa ha kema napo` = "I ate" (lit. "I eat past").
- `wa ha ka nase` = "I will go."

---

## 7. Numbers

Base‑10, perfectly regular. Digits are one syllable; powers of ten are their own
short words.

`so`0 `ta`1 `ne`2 `ki`3 `fo`4 `pe`5 `lu`6 `si`7 `mo`8 `ku`9
`na`10 `to`100 `fu`1000

Build a number big‑part first, summing the pieces:

- `ne na ki` = 2·10 + 3 = **23**
- `ki to` = 3·100 = **300**
- `ne fu · ne na pe` = 2000 + 25 = **2025**

Numbers are modifiers, so they follow the noun: `tu ki` = "three houses".

> Decimals, fractions, ordinals, negatives, dates, and clock time are all
> specified in **[GRAMMAR-EXTRAS.md](GRAMMAR-EXTRAS.md)**.

---

## 8. Building words — so there's a word for everything

You almost never memorize a new word; you **build** it. Four layers, in order of
preference (full protocol in [COINAGE.md](COINAGE.md)):

### Layer 1 — Core roots
The lexicon ([lexicon.csv](lexicon.csv)): ~490 concepts, each in its onset‑family.
These are the atoms.

### Layer 2 — Compounds (the main engine)
Combine roots **head first** — the first root is *what it is*, the rest narrow it:

| Build | Result |
|---|---|
| `sa` (water) + `ti` (place) → `sa ti` | a pool / body of water |
| `kesu` (drink) + `se` (hot) → `kesu se` | a hot drink |
| `samu` (animal) + `sa` (water) → `samu sa` | a water animal |
| `tu` (house) + `fila` (book) → `tu fila` | a library |

### Layer 3 — Semantic heads (regular derivation)
A few roots are conventionally used as "heads" — no special affixes to learn:

| Head | Pattern | Example |
|---|---|---|
| `pa` person | "one who ___" | `pa fapi` = teacher |
| `ti` place | "place of ___" | `ti famu` = school |
| `teku` tool | "device for ___" | `teku mi` = camera |
| `te` thing | "thing that/for ___" | `te kopi` = toy |
| `niso` ‑ness | "quality of ___" | `niso lefu` = strength |
| `noli` opposite | "reverse of ___" | `noli kipa` = to end |

### Layer 4 — Borrowing (proper nouns & untranslatables)
Transliterate into Faleni sounds and mark with **`ji`** (the name marker), so the
word is never mistaken for a compound:

- *Tokyo* → `ji tokijo` · *Claude* → `ji kolote` · *America* → `ji amelika`

**Transliteration:** map each foreign sound to the nearest Faleni letter
(`r`→`l`, `v`→`f`/`w`, `g`→`k`, `b`→`p`, `d`→`t`, `th`→`t`/`s`); break clusters
and final consonants with a vowel (default `o`/`i`); drop sounds Faleni lacks.

> **Preference order:** compound > derivation > borrowing. Borrow only for proper
> names or genuinely arbitrary terms.

---

## 9. Why this is "efficient" in the information‑theory sense

- **Channel‑robust:** wide phonetic spacing + self‑segregating `(C)V` + first‑
  syllable stress = high resistance to mishearing. We did **not** chase maximal
  compression — Shannon tells us an over‑compressed code has no error margin.
- **Low learning entropy:** few exception‑free rules ⇒ the whole grammar has a
  tiny description length. That *is* "easy to learn".
- **Productive, not memorized:** meaning composes, so the effective vocabulary is
  far larger than the root count. ~490 roots already express thousands of ideas.
- **Effort tracks frequency:** common things are short, rare things are long, so
  average message length is near‑minimal for real usage.

---

## 10. Status & roadmap

**v0.3 (now):** sounds, the onset‑family architecture, grammar, numbers,
derivation, borrowing, a ~490‑root / 527‑entry a priori lexicon, validator tool. Name verified
not to be an existing language.

Natural next steps:

1. **Grow the lexicon** toward ~600 roots (kinship, emotions, science, weather,
   cooking, abstract relations) using [COINAGE.md](COINAGE.md) + the validator —
   each new word coined into its onset‑family.
2. **Fix the number tail:** decimals, fractions, ordinals, dates, clock time.
3. **Optional aspect markers** (started / ongoing / finished) as opt‑in
   particles, kept out of the core on purpose.
4. **A Faleni ⇄ English translator / generator** built on `lexicon.csv`.
5. **A reference text** (a translated short story) to stress‑test the design.

Everything above is additive — none of it changes the 10 core rules.
