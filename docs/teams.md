# Choosing a team

One release, two looks. Pick one **when you build** — a Dial Panel keeps its
team for life. Body, trim, dial and gold are identical; only the light changes.

| | **A · IGNITION** | **B · NIGHTFALL** |
|---|---|---|
| It's… | a sunrise | a starfield |
| Band insert | `stl/ignition/04a-band-insert-ignition.stl` — ember perforation | `stl/nightfall/04b-band-insert-nightfall.stl` — starfield perforation |
| Screen | banded sun on a warm grid | stars over a cyan grid on deep violet |
| LED light | torch `#FF7A1A`, warm | violet `#7B2FF7` (grid light cyan `#22E8E0`) |
| Suits | an entryway or kitchen: it greets you | a hallway or living room at night |

Set the team once in the dashboard's config (`team = "ignition"` or
`team = "nightfall"`); it selects the screen palette and the LED colour.

> **Pending:** the dashboard software (dial navigation, the idle reset,
> the team palette, LED control) is not written yet. The hardware, the
> overlays in `config.txt` and this setting's meaning are fixed; the app
> that reads it is the next piece of work.

**Rules the release keeps** (from the xxx5 guide): colour is light, never
paint on the body; colour never carries state — focus is a white ring, the
idle reset says "HOME IN n"; one gold mark; no blends of the two teams.
