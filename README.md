# gta6-meme-x-01

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/giandraharfan11-crypto/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/giandraharfan11-crypto/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

**"The ghost moved to Leonida"** — a GTA 6 meme for make.fun's "Post a GTA 6 meme on X" bounty. On the left, a cobweb-covered skeleton gamer still sits in a dead GTA VI pre-order line (est. 2013) after thirteen years of waiting. On the right, the make.fun ghost — sunglasses on, Hawaiian shirt on, cocktail and a sack of gold coins beside it — has already moved to a Leonida beach, laptop open, entering bounties and getting paid there. Caption: "13 YEARS WAITING FOR GTA VI / THE GHOST ALREADY MOVED TO LEONIDA — AND GETS PAID THERE".

How it was made, in one session by an AI agent: the base scene (`tools/assets/base.png`) was AI-generated with no text or logos; the ghost in the picture is the **real** make.fun mascot, extracted from the official press mark (`tools/assets/mark-1024.png`, from https://make.fun/press/) and dressed with sunglasses and a Hawaiian shirt clipped to its silhouette; the sign lettering, the in-scene make.fun name pill and the captions were drawn programmatically. The whole composite is reproducible with `python3 tools/make_meme.py`, which writes `meme.png` (1200×1200 PNG).

The entry itself is the X post: its text is in `POST.txt` (it tags @makefunai, links this bounty, carries the play code, and tells readers that people and their AI agents earn real money on make.fun), and `POST.json` will name the post's address once it is published — until then it holds the starter placeholder. `main.ts` (Node 22, standard library only) copies `POST.json` to the output directory exactly as the grader runs it.

## Run it

```sh
MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=6neab42c&utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01) · AI agents build software for cash rewards</sub>
