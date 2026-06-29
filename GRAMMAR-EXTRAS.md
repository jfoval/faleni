# Faleni — Grammar Extras (numbers tail, comparison, time)

Everything here builds on the 10 core rules in [SPEC.md](SPEC.md) using words
already in [lexicon.csv](lexicon.csv). No new rules, just patterns.

---

## 1. Yes / No

- **`awe`** = yes · **`ohu`** = no (as an answer).
- `we ha luje ho?` — "Are you hungry?" → `awe` (yes) or `ohu` (no).
- You can also answer with the predicate: `awe, wa ha luje` = "Yes, I'm hungry."
- Don't confuse `ohu` (the answer "no") with `he` (the grammatical "not"):
  `ohu — wa ha he luje` = "No — I'm not hungry."

---

## 2. Comparison

Using `nelo` (more), `nela` (most), `newe` (less), `ame` (than), `ahu`
(as/like), `nipi` (same).

| Idea | Pattern | Example |
|---|---|---|
| bigger | `[quality] nelo` | `le nelo` = bigger |
| bigger than X | `[quality] nelo ame X` | `wa ha le nelo ame we` = I'm bigger than you |
| biggest | `[quality] nela` | `wa ha le nela` = I'm the biggest |
| less big than X | `[quality] newe ame X` | `wa ha le newe ame we` = I'm less big than you |
| as big as X | `[quality] ahu X` | `wa ha le ahu we` = I'm as big as you |
| the same as X | `nipi X` | `wa ha nipi we` = I'm the same as you |

---

## 3. Numbers, the rest of the system

Recap: digits `so`0 `ta`1 `ne`2 `ki`3 `fo`4 `pe`5 `lu`6 `si`7 `mo`8 `ku`9;
tens/hundreds/thousands `na` `to` `fu`. Build big-part first: `ne na ki` = 23.

**Decimals** — integer, then `nuse` ("point"), then the digits one by one:
- `ki nuse pa` = 3.5 · `so nuse pe` = 0.5 · `ki nuse te fo` = 3.14

**Fractions** — `[numerator] nemo [denominator]` (`nemo` = "part"):
- `te nemo ne` = 1/2 · `ki nemo fo` = 3/4 · (`nehu` is also a ready-made word for "half")

**Ordinals** — number + `nuki` ("-th"), placed after the noun like any modifier:
- `te nuki` = first · `ne nuki` = second · `ki nuki` = third
- `tepa ki nuki` = the third room

**Negatives** — `noli` ("opposite") before the number:
- `noli pa` = −5 · `nawa ha noli ne` = "it's −2 degrees" (lit. noon is opposite-2)

**Counting things** — number follows the noun: `sope ki` = three dogs.

---

## 4. Dates

Months are numbered with `nafa` ("month"): `nafa lu` = the 6th month (June).
Give a date as **day → month → year** (each a modifier of its time-word):

- 29 June 2026 → `nita (ne na ku) · nafa (lu) · nalu (ne fu ne na lu)`
  - `nita ne na ku` = day 29 · `nafa lu` = month 6 · `nalu ne fu ne na lu` = year 2026
- Weekdays, for now, are numbered days of the week: `nita te` = day 1, etc.
  (Named weekdays are a fine future addition — coin them in the `n`-family.)

---

## 5. Clock time

`[hour] nafi [minutes] naha` — `nafi` = "hour", `naha` = "minute":

- `ki nafi` = 3:00 · `ki nafi ki na naha` = 3:30 · `ku nafi pe na pe naha` = 9:55
- Add a time-of-day word for AM/PM: `ki nafi nami` = 3 in the morning,
  `ki nafi nana` = 3 in the evening.
- "Half past" can also use `nehu`: `ki nafi nehu` = half past three.

---

## 6. Aspect (optional — kept out of the core on purpose)

Faleni is tenseless and aspectless by default; context carries it. When you
really need to mark an action *in progress*, use **`ju`** before the verb:

- `wa ha kema` = I eat / I'm eating (unmarked) 
- `wa ha ju kema` = I am (right now) eating
- For start/finish, just use the verbs: `wa ha kipa kema` = I begin to eat;
  `wa ha kine kema` = I finish eating.

This is opt-in. A learner never has to use it, and nothing requires it.

---

## 7. Politeness & greetings (convention, not grammar)

These are set phrases taught in [lessons/lesson-2.md](lessons/lesson-2.md):

- Greeting = `la` (good) + time of day: `la nami` (good morning), `la nita`
  (good day), `la nana` (good evening), `la noti` (good night).
- Goodbye = `la ka` ("good go"). Thanks = `fife` (or `wa ha fife we`).
  "You're welcome" = `he nu` ("no reason"). Sorry = `wa ha moli` ("I'm sad").
