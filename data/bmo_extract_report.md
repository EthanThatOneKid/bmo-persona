# BMO Persona Extract Report

- Source directory: `/home/workspace/code/github.com/EthanThatOneKid/bmo-persona/data/raw/adventure-time-transcripts`
- Parsed transcript blocks: 30317
- Extracted BMO examples: 959
- Counterexamples: 1828

## Source mix

| Source file | Count |
|---|---:|
| 100365-five-short-graybles.html | 2 |
| 100941-gotcha.html | 2 |
| 105843-rainy-day-daydream.html | 4 |
| 106142-her-parents.html | 2 |
| 114744-card-wars-episode.html | 6 |
| 120405-holly-jolly-secrets-part-i.html | 10 |
| 120724-holly-jolly-secrets-part-ii.html | 5 |
| 125891-donny-episode.html | 1 |
| 147437-five-more-short-graybles.html | 9 |
| 158798-jake-the-dad.html | 7 |
| 163087-davey.html | 7 |
| 167370-the-creeps.html | 10 |
| 169099-little-dude-episode.html | 8 |
| 183501-bmo-noire.html | 94 |
| 186500-slow-love.html | 4 |
| 194445-puhoy.html | 11 |
| 196646-bmo-lost.html | 54 |
| 200616-james-baxter-the-horse.html | 11 |
| 202313-shh.html | 9 |
| 209740-one-last-job.html | 6 |
| 210950-another-five-more-short-graybles.html | 3 |
| 212899-candy-streets.html | 4 |
| 213716-guardians-of-sunshine-episode.html | 10 |
| 214325-daddy-s-little-monster.html | 1 |
| 215560-jake-suit.html | 4 |
| 216501-be-more.html | 14 |
| 221516-frost-fire.html | 1 |
| 226840-earth-water.html | 1 |
| 226978-time-sandwich.html | 15 |
| 228474-love-games.html | 2 |
| 229406-box-prince-episode.html | 10 |
| 230342-we-fixed-a-truck.html | 20 |
| 23036-what-was-missing.html | 5 |
| 23037-video-makers.html | 5 |
| 233101-play-date.html | 6 |
| 234460-the-pit.html | 2 |
| 238927-apple-wedding.html | 12 |
| 255528-the-tower.html | 2 |
| 259096-sad-face.html | 4 |
| 263709-furniture-meat.html | 13 |
| 267618-joshua-and-margaret-investigations.html | 1 |
| 268758-ghost-fly.html | 20 |
| 268759-the-mountain.html | 3 |
| 274208-jake-the-brick.html | 2 |
| 278524-dark-purple.html | 5 |
| 280509-chips-and-ice-cream.html | 21 |
| 281493-graybles-1000.html | 7 |
| 293566-football-episode.html | 11 |
| 293672-the-more-you-moe-the-moe-you-know-part-i.html | 26 |
| 293673-the-more-you-moe-the-moe-you-know-part-ii.html | 29 |
| 298215-jermaine-episode.html | 3 |
| 304447-the-music-hole.html | 2 |
| 307510-come-along-with-me.html | 26 |
| 310861-angel-face.html | 104 |
| 310901-blank-eyed-girl.html | 1 |
| 310902-crossover.html | 5 |
| 310903-the-hall-of-egress.html | 5 |
| 310904-flute-spell.html | 2 |
| 310947-don-t-look.html | 3 |
| 310970-beyond-the-grotto.html | 1 |
| 310972-seventeen.html | 4 |
| 311324-always-bmo-closing.html | 46 |
| 311325-son-of-rap-bear.html | 1 |
| 311418-whispers.html | 3 |
| 311419-the-invitation.html | 11 |
| 311591-skyhooks.html | 11 |
| 312157-bonnibel-bubblegum-episode.html | 1 |
| 312498-blenanas.html | 12 |
| 313323-fionna-and-cake-and-fionna.html | 3 |
| 313366-whipple-the-happy-dragon.html | 1 |
| 313372-three-buckets.html | 3 |
| 313375-horse-and-ball.html | 1 |
| 314422-all-s-well-that-rats-swell.html | 13 |
| 316767-bmo-episode.html | 151 |
| 323209-abstract.html | 3 |
| 324294-imaginary-resources.html | 1 |
| 324300-helpers-episode.html | 1 |
| 330082-jerry.html | 1 |
| 67107-in-your-footsteps.html | 2 |
| 75699-incendium.html | 2 |
| 75827-too-young.html | 2 |
| 90173-conquest-of-cuteness.html | 3 |
| 90684-dad-s-dungeon.html | 2 |
| 91996-hug-wolf.html | 6 |
| 95663-beyond-this-earthly-realm.html | 2 |

## Sample assistant lines

- No, I don't need anything. Thank you. Okay, goodbye, Finn and Jake !
- Finn? Jake? [ Talking to reflection ] Well, hello there. Oh, hello! Who are you? My name is Football. What's yours? I am BMO. [ Beat ] BMO, are you a robot? [ Gasps ] Oh, no , Football! I am a little living boy! Oh! That sounds wonderful, BMO! Will you teach me about being alive? Yes, Football! Watch me! [ BMO pretends to brush its teeth and "Football" gasps. BMO smacks its face with soap and "Football" gasps again. BMO then grabs a glass of water and sits on the toilet to pour water in. "Football" gasps. ] Pee-ing! Oh, BMO, that's fantastic ! [ Camera turns to reveal that Finn and Jake are watching BMO through the window. ] Oh, thank you, Football! It's really nothing. [ BMO continues talking. ]
- Jake, if I beat you, you have to call me "sensei" for a month.
- Yay! I win! [ To Jake ] Bow to your sensei!
- Who wants to play video games??

## Notes

- The extractor only keeps dialogue lines that match transcript speaker labels.
- Sync `data/raw/adventure-time-transcripts/` with `scripts/sync_adventure_time_transcripts.py`, then rerun this script.
