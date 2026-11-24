# [Game title] ([publisher], [year]): verified reverse engineering

[One paragraph: what the game is, who made it (programming, graphics, sound), which release was studied.]

## Release studied

| File | SHA-256 |
|---|---|
| `[image].dsk` | `[hash]` |

[Original or conversion? By whom? What in the loading sequence is not from the original?]

## Getting started

Requirements: Python 3.9+, `pip install -e ../cpc-game-archaeology` (installs `cpcarch` and SkoolKit 10.2).

    python3 extract.py path/to/your/[image].dsk     # writes build/, checks every hash
    python3 make_all.py                             # regenerates everything and runs the verifications

## Findings

| Subsystem | Document | Verification |
|---|---|---|
| | | |

## Status and what remains

## Credits

Game: [authors], [publisher]. Study: [contributors]. [Disclose AI assistance if any.]

Code under MIT, documentation under CC BY 4.0. No game material is distributed.
