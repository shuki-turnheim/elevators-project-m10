# Phase 2: Scrolling

Phase 1 (`ScreenLayout`) separates **world size** (full building) from **viewport size** (window, clamped by min/max). When the building is larger than the viewport, `needs_scroll_x` / `needs_scroll_y` are set and a warning is logged; content may be clipped until scrolling exists.

## Goal

Allow vertical and horizontal navigation when:

- `world_width > viewport_width` or `world_height > viewport_height`, and
- `floors_count > SCROLL_FLOORS_THRESHOLD` or `elevators_count > SCROLL_ELEVATORS_THRESHOLD` (from `.env`).

## Camera model

Add to `ScreenLayout` or a small `Camera` object:

- `scroll_x`, `scroll_y` (pixels, 0 .. world - viewport)
- Clamp scroll so the viewport never shows empty space beyond the building.

## Input

- Mouse wheel: vertical scroll; Shift+wheel or horizontal wheel: horizontal scroll
- Arrow keys (optional): pan viewport

## Rendering

For each draw call (`blit`, `draw.line`, `draw.circle`, `fill` rect):

- World position `(wx, wy)` → screen position `(wx - scroll_x + content_offset_x, wy - scroll_y + content_offset_y)`
- When scroll is active, `content_offset_*` for centering is typically 0 (building larger than window).

Alternative: draw the full building to an off-screen `world_surface`, then `screen.blit(world_surface, (-scroll_x, -scroll_y))` each frame. Simpler hit-testing requires a single coordinate transform helper.

## Hit testing

`Manager.call` uses `pg.mouse.get_pos()` in **screen** coordinates. Convert before comparing to floor buttons:

```text
world_x = screen_x + scroll_x - content_offset_x
world_y = screen_y + scroll_y - content_offset_y
```

Or store button centers in world space and transform mouse into world space with the same helper.

## Files to touch

- `screen.py` — scroll state, clamp, helpers `world_to_screen` / `screen_to_world`
- `game.py` — handle scroll events in the main loop
- `manager.py` — mouse transform in `call`
- `floor.py`, `elevator.py` — use transform for all drawing and updates in the game loop (initial build can stay in screen space if scroll starts at 0; dynamic redraws must account for scroll)

## Estimated effort

Medium–high (~150–250 lines, regression risk on floor button clicks). Implement only after explicit approval.
