#!/usr/bin/env python3
"""gen_audio.py - generate CORRECT, NATURAL Faleni audio via a neural TTS that
honors phonemes (Azure AI Speech).

Faleni is perfectly phonemic, so each word maps to an EXACT IPA string
(faleni -> /'fa.le.ni/). A neural voice that accepts IPA renders exactly those
sounds, correctly AND naturally -- no English letter-guessing. We render once,
commit the clips, and every visitor hears the same correct audio.

SETUP (one time):
  1. portal.azure.com -> create a "Speech" resource (free F0 tier).
  2. Open it -> "Keys and Endpoint" -> copy KEY 1 and the Region (e.g. eastus).
  3. Save them in a gitignored file at the repo root named `.faleni_tts`:
         AZURE_TTS_KEY=your_key_here
         AZURE_TTS_REGION=eastus
     (or export AZURE_TTS_KEY / AZURE_TTS_REGION as env vars)

RUN:
  python3 site/build.py            # build (creates the data-say list)
  python3 tools/gen_audio.py       # writes site/assets/audio/<slug>.mp3
  python3 site/build.py            # rebuild so audio is copied into dist/
  git add -A && git commit ...      # commit the audio (CI/Linux can't synth)

Voice: set FALENI_VOICE (default en-US-JennyNeural; try en-US-AvaMultilingualNeural).
"""
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "site", "dist")
OUT = os.path.join(ROOT, "site", "assets", "audio")

# Faleni letters ARE their IPA values (that's the point of a phonemic spelling).
IPA = {c: c for c in "aeiouptkfshmnlw"}
IPA["j"] = "j"                                   # Faleni j = IPA /j/ ("y")
SYL = re.compile(r"[ptkfshmnlwj]?[aeiou]")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def ipa_word(w):
    """One Faleni word -> IPA with primary stress on the first syllable."""
    parts = []
    for s in SYL.findall(w):
        onset = IPA[s[0]] if len(s) > 1 else ""
        parts.append(onset + IPA[s[-1]])
    return "ˈ" + ".".join(parts)            # 'ˈ' + syllables joined by '.'


def ssml(text, voice):
    chunks = []
    for w in text.lower().split():
        w = re.sub(r"[^a-z]", "", w)
        if w:
            chunks.append('<phoneme alphabet="ipa" ph="%s">%s</phoneme>' % (ipa_word(w), w))
    return ('<speak version="1.0" xml:lang="en-US"><voice name="%s">%s</voice></speak>'
            % (voice, " ".join(chunks)))


def creds():
    cfg = {}
    path = os.path.join(ROOT, ".faleni_tts")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    return (os.environ.get("AZURE_TTS_KEY", cfg.get("AZURE_TTS_KEY")),
            os.environ.get("AZURE_TTS_REGION", cfg.get("AZURE_TTS_REGION")))


def synth(text, key, region, voice):
    url = "https://%s.tts.speech.microsoft.com/cognitiveservices/v1" % region
    req = urllib.request.Request(
        url, data=ssml(text, voice).encode("utf-8"), method="POST",
        headers={"Ocp-Apim-Subscription-Key": key,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
                 "User-Agent": "faleni-gen"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def data_say_values():
    vals = set()
    pat = re.compile(r'data-say="([^"]+)"')
    for fn in os.listdir(DIST):
        if fn.endswith(".html"):
            with open(os.path.join(DIST, fn), encoding="utf-8") as f:
                vals.update(pat.findall(f.read()))
    return sorted(v for v in vals if v.strip())


def main():
    key, region = creds()
    voice = os.environ.get("FALENI_VOICE", "en-US-JennyNeural")
    if not key or not region:
        print("Missing Azure creds. Put AZURE_TTS_KEY and AZURE_TTS_REGION in a "
              "`.faleni_tts` file at the repo root (or env vars). See this file's header.")
        return 1
    if not os.path.isdir(DIST):
        print("Run `python3 site/build.py` first.")
        return 1
    os.makedirs(OUT, exist_ok=True)
    vals = data_say_values()
    print("Generating %d clips (voice %s)..." % (len(vals), voice))
    made = skipped = 0
    for v in vals:
        path = os.path.join(OUT, slug(v) + ".mp3")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            skipped += 1                          # resume: keep already-generated clips
            continue
        for attempt in range(6):
            try:
                audio = synth(v, key, region, voice)
                with open(path, "wb") as f:
                    f.write(audio)
                made += 1
                time.sleep(0.4)                   # stay under the free-tier rate limit
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 5:
                    time.sleep(2 ** attempt)      # backoff: 1, 2, 4, 8, 16s
                    continue
                print("  FAILED %-16s HTTP %s" % (v, e.code))
                break
            except Exception as e:
                print("  FAILED %-16s %s" % (v, str(e)[:80]))
                break
    print("Done: %d new, %d already present -> %s" % (made, skipped, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
