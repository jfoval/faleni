# Faleni — an efficient, learnable, fully original language

**Faleni** (from *fa* "speak" + *leni* "easy" = *the easy tongue*) is a
constructed language engineered around one idea:

> Maximize what you can say per unit of effort to learn and effort to speak,
> while keeping **zero exceptions** and a **systematic way to invent a word for
> anything**.

It draws on what linguistics, information theory, and decades of constructed‑
language experiments (Esperanto, Lojban, Toki Pona, and the 1600s "philosophical
languages") actually taught us — keeping what works, discarding the parts that
just make languages hard.

Every root is **invented from scratch** (*a priori*) — nothing is borrowed from
English or any other language, so Faleni is its own language and is culturally
neutral. The name was checked online: it is **not** an existing language.

---

## Why it's easy

Things natural languages make you memorize that Faleni simply **does not have**:

- ❌ Irregular verbs (*go → went*), irregular plurals (*mouse → mice*)
- ❌ Grammatical gender (no arbitrary masculine/feminine)
- ❌ Silent letters or spelling that disagrees with sound
- ❌ Noun cases, verb conjugation tables, agreement
- ❌ Articles (*a / the*), tone, vowel‑length traps
- ❌ Idioms that don't mean the sum of their parts

What's left is a language whose **entire grammar is ~10 rules**, every word is
spelled exactly as it sounds, and **every word never changes shape**.

## The trick that makes invented words learnable: the onset tells the domain

Because the roots are invented, we could give them *structure*. **The first
sound of every content word marks its meaning‑domain:**

| Starts with | Domain | Examples |
|---|---|---|
| `p` | people & body | `pa` person, `pama` mother, `pika` head |
| `m` | mind & feeling | `me` want, `mi` see, `masu` happy |
| `s` | nature | `sa` water, `su` sun, `sena` moon |
| `t` | things & places | `te` thing, `tu` house, `tuna` city |
| `k` | actions | `ka` go, `ke` make, `kema` eat |
| `l` | qualities & color | `la` good, `le` big, `lasa` red |
| `f` | speech & info | `fa` speak, `fe` word, `fila` book |
| `n` | number, time, relation | `no` time, `nita` day, `ni` amount |
| vowel | logic & connectives | `a` all, `u` very, `isa` if |
| `h` `j` | grammar words | `ha` is, `he` not, `jo` plural |
| `w` | pronouns | `wa` I, `we` you, `wi` they |

You never think about this while *speaking* (so it costs nothing to use) — but it
makes the vocabulary feel coherent, and it's the **recipe for coining new
words**: a new nature‑thing starts with `s`, a new action with `k`. (We fix only
the *first* consonant, not the whole word — the 1600s languages that encoded
meaning into every letter became impossible to tell apart by ear.)

## Why it's efficient

- **Frequency‑weighted length** — the most common ~50 ideas are one syllable;
  rare ones are longer. (Zipf's law of abbreviation, made a rule.)
- **Categoryless roots** — one root works as noun, verb, or adjective by
  position, so you memorize one word, not four.
- **Self‑segregating sound** — every syllable is (consonant +) vowel, so word
  boundaries are unambiguous by ear.
- **Compositional vocabulary** — most words are *built* from a small core, not
  memorized.
- **Tuned redundancy** — not maximally compressed (that's fragile over noise);
  sounds are spaced to stay distinct when misheard.

## Why it never runs out of words

Faleni has a **vocabulary engine**, not just a word list:

1. A small set of **core roots** (the seed lexicon), each in its onset‑family.
2. **Compounding rules** to combine them transparently.
3. A handful of **semantic heads** (person, place, tool, ‑ness, opposite…) for
   regular derivation.
4. A **borrowing protocol** for proper nouns and technical terms.
5. A machine‑checkable **registry** ([`lexicon.csv`](lexicon.csv)) + a
   **validator** so new words are always legal, in the right family, and never
   collide.

See [COINAGE.md](COINAGE.md) for the full "keep adding words" system.

---

## 60‑second taste

| Faleni | Literal | Meaning |
|------|---------|---------|
| `wa ha mu we` | I `is/does` love you | I love you. |
| `we ha fa ho?` | you `is/does` speak `?` | Do you speak? |
| `wi ha he kema` | they `is/does` not eat | They don't eat. |
| `tu wa ha le` | house my `is/does` big | My house is big. |
| `we ha me kema jeta?` | you `is/does` want eat what | What do you want to eat? |
| `wa jo ha ka tuna` | I many `is/does` go city | We go to the city. |

Build a word you've never seen (head first):

- `pa` (person) + `fapi` (teach) → **`pa fapi`** = *teacher*
- `teku` (tool) + `mi` (see) → **`teku mi`** = *camera*
- `teku` (tool) + `fa` (speak) → **`teku fa`** = *phone*
- `niso` (‑ness) + `la` (good) → **`niso la`** = *goodness*
- `noli` (opposite) + `kapi` (open) → **`noli kapi`** = *to close*

---

## Files

- **[lessons/](lessons/)** — the course; start with **[Lesson 1](lessons/lesson-1.md)**.
  The friendliest way to *learn* Faleni.
- **[SPEC.md](SPEC.md)** — the full specification (sounds, onset‑family
  architecture, grammar, word‑building) — the reference.
- **[GRAMMAR-EXTRAS.md](GRAMMAR-EXTRAS.md)** — numbers tail (decimals, fractions,
  dates, clock), comparison, yes/no, optional aspect.
- **[compounds.md](compounds.md)** — ~100 ready-made compounds and the pattern for
  thousands more.
- **[COINAGE.md](COINAGE.md)** — the protocol for inventing new words. Read this
  to *grow* Faleni.
- **[lexicon.csv](lexicon.csv)** — the living dictionary (~490 roots, 527 entries).
- **[tools/faleni.py](tools/faleni.py)** — validator + word generator + helper.

## Using the tool

```sh
python3 tools/faleni.py            # validate the whole lexicon + show stats
python3 tools/faleni.py family     # the onset->domain legend + per-family counts
python3 tools/faleni.py free       # which 1-syllable forms are still free
python3 tools/faleni.py check masu # is "masu" legal? taken? which family?
python3 tools/faleni.py suggest s 40  # 40 fresh, clean nature-family forms to coin from
```

## Status

**v0.3 — teachable foundation.** ~490 a priori roots (527 entries, 0 collisions),
the number tail closed ([GRAMMAR-EXTRAS.md](GRAMMAR-EXTRAS.md)), a compound
reference, and a 3‑lesson course. Enough to hold simple conversations and teach.
Next steps: keep growing the lexicon in curated batches, then a website/wiki
generated from `lexicon.csv` and a learning app. See the roadmap in [SPEC.md](SPEC.md).
