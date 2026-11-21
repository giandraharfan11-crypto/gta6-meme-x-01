// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry itself is a public post on X: a GTA 6 meme whose picture
// carries the make.fun ghost. This program's whole job is to hand the
// post's address to the grader: it copies POST.json from the repository
// root into the output directory, byte for byte, and prints nothing on
// success. It is deterministic -- two runs write identical bytes -- and
// it touches no network, no clock, and no file outside the two
// directories named by the environment.
//
//   MAKEFUN_BOT_DIR    repository directory (default /bot)
//   MAKEFUN_OUTPUT_DIR output directory     (default /output)
//
// Local check:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outputDir, { recursive: true });

try {
  copyFileSync(join(botDir, "POST.json"), join(outputDir, "POST.json"));
} catch (err) {
  const reason = err instanceof Error ? err.message : String(err);
  console.error(`could not copy POST.json from ${botDir}: ${reason}`);
  process.exit(1);
}
