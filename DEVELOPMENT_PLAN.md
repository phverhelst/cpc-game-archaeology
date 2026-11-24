# Designing and planning a game like Antiriad: a generic development plan

This document proposes a development plan for an action and exploration game like *The Sacred Armour of Antiriad*, independent of language and platform. It is reconstructed from what the game's code shows, not from testimony: how Palace Software actually worked in 1986 (development hardware, tools, schedule) still has to be documented from sources. Each step is therefore set against what Antiriad shows, with addresses and figures established in the `cpc-game-archaeology-antiriad` repository.

## The starting point: the constraint, not the character

The natural reflex is to start with what can be seen: make the character walk, jump and attack, then build out from there. That is the reflex of a player, and of someone who no longer works under hardware constraints. It suits a throwaway prototype of a few days. It does not suit a foundation, for two reasons. First, the structuring choices (size of the world, scrolling or fixed screens, number of simultaneous objects, graphics mode) follow from the machine's budget and must be made before any code is written. Second, a hero programmed as a special case will have to be rewritten when enemies are added. In Antiriad the hero, Tal, is not a special case: he is slot 0 of a table of eight 19-byte object records (&B400), driven by the same engine of states, scripts and animations as the enemies.

The proposed order therefore goes from budget to skeleton, from skeleton to a generic object of which the hero is the first instance, then to a vertical slice, to data-driven production, and finally to finishing.

## The seven steps

| Step | Deliverable | Exit criterion | What Antiriad shows |
|---|---|---|---|
| 1. Framing | Memory budget, time budget per frame, screen format, division of the world | A written memory map where every area has a size ceiling | 64 KB, 16 of them for the screen; a 20 ms frame (79 872 T-states); mode 0 for play and mode 1 for the panel; 69 fixed rooms, no scrolling; rooms and sprites in &0200-&53FF, about 20 KB |
| 2. Skeleton | Fixed-step main loop, interrupts, one room on screen, measurement of time used | The loop runs at a constant rate with a measured margin | Main loop &54FA; 300 Hz interrupt (&6EF2) that switches mode and palette mid-screen and calls the sound driver at 100 Hz |
| 3. Generic object and hero | Object record, states, transitions, animations, collisions with the scenery, room changes | The hero walks, jumps and shoots pleasantly; room changes leak nothing | 19-byte records (&B400), state table (&922A), scripts (&97F8), animations (&9021), sprites (&9432); a single speed table for the jump, read one way to rise and the other to fall |
| 4. Vertical slice | A few fully playable rooms: an enemy, the key object, the panel, a sound | The slice is fun to play; otherwise back to step 3 | The armour, the panel (lines 136 to 199) and its gauges; the sound driver |
| 5. Data-driven production | Frozen data formats, input tools, content made in parallel (rooms, enemies, sounds) | The code stops growing; only data grow | Object lists per room (&9BC7), enemies driven by scripts, music as bytecode read by the driver at &755E |
| 6. Overall rules | Energy, radiation, collectables, end of game, title screen | A game can be played from start to finish | The two-second interrupt task (&6F18) for life and radiation; the ending at &5C31 |
| 7. Finishing | Balancing, effects, loader, testing | No blocking defects; the budget holds | The final implosion: one CRTC register write and a loop of random draws, a cheap effect added once the budget was known |

## The role of each step

Framing is paper work. It fixes what the machine allows and what the game will do with it. On a modern platform the words change (time per frame, video memory, asset size, target platforms), but the question remains: what will be impossible to change later? A scrolling engine would have eaten Antiriad's budget; the choice of fixed screens made everything else possible.

The skeleton shows almost nothing, but carries everything. A fixed-step loop makes the game deterministic, hence testable: that determinism is what allowed every model in the Antiriad study to be checked against the game, turn by turn. Measuring time used from the start avoids discovering too late that a frame has been overrun.

The generic object is where the character's movements belong. Walking, jumping and attacking are states of an object, with their animations and their transition rules. Fine tuning (speed tables, jump height, animation lengths) takes many trials: play, adjust, play again. Room changes come right after, because they fix the shape of the world.

The vertical slice is the moment of truth. A few rooms, complete, with everything the final game will contain, in small. If it is not fun, producing 69 rooms will not change that. If it is, the rest becomes production.

Data-driven production lets work proceed on three parallel tracks: code builds the tools and mechanics, graphics produce sprites and rooms, sound writes for the driver. The condition is that data formats are frozen early. Antiriad shows this everywhere: the sound driver interprets bytes, enemies follow scripts, rooms are lists. The title screen credits name exactly these three tracks: programming (Andrew Fitter), plot and graphics (Daniel Malone), sound design (Richard Joseph).

Overall rules and finishing come last, because they depend on everything else and because the available margin is only known once the content is in place.

## What is generic

Nothing in this plan depends on the Z80 or the CPC. It comes down to five principles:

- decide the constraints before writing code;
- build a fixed-step, measured skeleton;
- treat the hero as the first client of a generic object system;
- validate the fun on a complete slice before producing content;
- grow the data rather than the code.

On a modern machine the constraint no longer comes from the hardware. You then have to set it yourself (a time budget, a world size, a number of objects), or the project grows without shape.
