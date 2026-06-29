# Contributing to Faleni

Faleni grows by **proposal and review**, not by free editing. That is on purpose:
an open, anyone-can-edit wiki is the fastest way to wreck a constructed language
(fifteen words for "dog", broken sounds, lost regularity). The curation model
protects the very things that make Faleni worth learning — its **regularity** and
its **originality**.

The good news: a machine does most of the gatekeeping for you.

## The pipeline

```
propose  ->  auto-validate (faleni.py in CI)  ->  maintainer review  ->  merge
```

Every pull request that touches `lexicon.csv` runs the validator in CI. A word
that is illegal, collides, or is a near-homophone of an existing word **fails the
check before a human looks at it** — so you get instant, objective feedback.

## Add a word in four steps

1. **Build before you invent.** Most concepts are a compound of existing words
   (see [compounds.md](compounds.md)). A real new *root* is rare.
2. **Pick the right family.** A content word's first sound marks its domain
   (`p` people, `m` mind, `s` nature, `t` things, `k` actions, `l` qualities,
   `f` speech, `n` number/time/space, vowel = logic). See [COINAGE.md](COINAGE.md).
3. **Validate locally:**
   ```sh
   python3 tools/faleni.py check siso     # legal? taken? right family? too close?
   python3 tools/faleni.py suggest s 40   # menu of fresh nature-family forms
   ```
4. **Open a pull request** adding one line to `lexicon.csv`:
   ```
   siso,root,snow,,nature,
   ```
   Columns are `word,type,gloss,decomp,domain,notes`. No commas inside fields.

> **Maintainers:** the CI check *reports* pass/fail on the PR, but GitHub only
> *blocks* a red merge once you enable a branch-protection rule on `main`
> (Settings → Branches → require the **Validate lexicon** status check). Turn that
> on to make the gate hard rather than advisory.

## What reviewers check

- The validator passed (CI flags any failure right on the PR).
- The word is genuinely needed (not buildable as a clean compound).
- The gloss is clear and the family is right.
- It isn't easily confused by ear with a common word, especially its opposite.

## Other contributions

Lessons, example texts, translations, bug fixes to the site or `faleni.py`, and
new helper tooling are all welcome by ordinary pull request — no lexicon rules
apply to those.

## Local setup

```sh
python3 tools/faleni.py            # validate the lexicon (zero dependencies)
pip install -r site/requirements.txt && python3 site/build.py   # build the website
open site/dist/index.html
```
