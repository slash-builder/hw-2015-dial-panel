//! Desktop harness for the Dial Panel's interaction model.
//!
//! The point is to iterate on how the panel *feels* without flashing a card and
//! walking to a Pi. The window is the panel's real geometry — the 7" Touch
//! Display 2 is a 720×1280 portrait panel mounted landscape, so 1280×720 — and
//! the keyboard and scroll wheel stand in for the dial.
//!
//! This is a test rig, not a decision. Which framework the shipped shell is
//! built on is THUN-24's benchmark to settle; nothing here should be read as
//! having chosen. What *is* shared with the device is [`dial_nav`] — the same
//! state machine, byte for byte, which is the whole reason it takes its input
//! as events and its time as ticks.
//!
//! ```text
//! ← →   or scroll     turn the dial
//! Enter / Space       push
//! Esc                 quit            (the device has no such key — see below)
//! ```
//!
//! There is deliberately no key here that acts as "back". The panel does not
//! have one, and a harness that quietly added one would be testing a device
//! nobody is building.

mod font;

use std::num::NonZeroU32;
use std::rc::Rc;
use std::time::{Duration, Instant};

use dial_nav::{Config, Event as NavEvent, Frame, Nav, Screen, Tile, TileKind, Value};
use tiny_skia::{Color, FillRule, Paint, PathBuilder, Pixmap, Rect, Stroke, Transform};
use winit::event::{ElementState, Event, MouseScrollDelta, WindowEvent};
use winit::event_loop::{ControlFlow, EventLoop};
use winit::keyboard::{Key, NamedKey};
use winit::window::WindowBuilder;

/// The panel, landscape.
const W: u32 = 1280;
const H: u32 = 720;

/// One team's light. Colour is light on this device, never paint, and it never
/// carries state — focus stays a white ring. Values from `docs/teams.md`.
struct Team {
    name: &'static str,
    light: Color,
    secondary: Color,
}

impl Team {
    fn ignition() -> Self {
        Self {
            name: "IGNITION",
            light: rgb(0xFF, 0x7A, 0x1A),
            secondary: rgb(0xFF, 0xB4, 0x6B),
        }
    }

    fn nightfall() -> Self {
        Self {
            name: "NIGHTFALL",
            light: rgb(0x7B, 0x2F, 0xF7),
            secondary: rgb(0x22, 0xE8, 0xE0),
        }
    }
}

fn rgb(r: u8, g: u8, b: u8) -> Color {
    Color::from_rgba8(r, g, b, 255)
}

// tiny-skia's colour constructors are not `const`, so these are functions.
fn ink() -> Color {
    rgb(10, 10, 13)
}
fn tile_bg() -> Color {
    rgb(26, 26, 31)
}
fn white() -> Color {
    rgb(255, 255, 255)
}
fn dim() -> Color {
    rgb(115, 115, 128)
}

fn demo_tiles() -> Vec<Tile> {
    vec![
        Tile::range("lamp", "LAMP", 0, 100, 5, "%"),
        Tile::range("heat", "HEATING", 5, 30, 1, "°"),
        Tile::toggle("mic", "MIC"),
        Tile::action("night", "GOODNIGHT"),
        Tile::info("outside", "OUTSIDE"),
    ]
}

fn panel() -> Nav {
    let mut nav = Nav::new(demo_tiles(), Config::default());
    // A little starting state, so the first frame is not all zeros.
    nav.set_value(0, Value::Number(40));
    nav.set_value(1, Value::Number(19));
    nav
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut team = Team::ignition();
    let mut shots: Option<String> = None;
    let mut args = std::env::args().skip(1);

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--team=nightfall" | "nightfall" => team = Team::nightfall(),
            "--team=ignition" | "ignition" => team = Team::ignition(),
            "--shots" => {
                shots = Some(args.next().ok_or("--shots needs a directory")?);
            }
            other => {
                eprintln!("unknown argument {other:?}");
                eprintln!("usage: dial-sim [ignition|nightfall] [--shots <dir>]");
                std::process::exit(2);
            }
        }
    }

    if let Some(dir) = shots {
        return write_shots(&dir, &team);
    }

    let mut nav = panel();
    let event_loop = EventLoop::new()?;
    let window = Rc::new(
        WindowBuilder::new()
            .with_title("Dial Panel — harness")
            .with_inner_size(winit::dpi::LogicalSize::new(W, H))
            .with_resizable(false)
            .build(&event_loop)?,
    );

    let context = softbuffer::Context::new(window.clone())?;
    let mut surface = softbuffer::Surface::new(&context, window.clone())?;
    let mut pixmap = Pixmap::new(W, H).ok_or("could not allocate the pixmap")?;

    let frame_time = Duration::from_millis(16);
    let mut last = Instant::now();
    let mut pending_scroll = 0.0_f32;

    event_loop.run(move |event, elwt| {
        elwt.set_control_flow(ControlFlow::WaitUntil(Instant::now() + frame_time));

        match event {
            Event::WindowEvent { event, .. } => match event {
                WindowEvent::CloseRequested => elwt.exit(),

                WindowEvent::KeyboardInput { event, .. } => {
                    if event.state != ElementState::Pressed {
                        return;
                    }
                    match event.logical_key {
                        Key::Named(NamedKey::ArrowRight) | Key::Named(NamedKey::ArrowDown) => {
                            nav.handle(NavEvent::Turn(1));
                        }
                        Key::Named(NamedKey::ArrowLeft) | Key::Named(NamedKey::ArrowUp) => {
                            nav.handle(NavEvent::Turn(-1));
                        }
                        Key::Named(NamedKey::Enter) | Key::Named(NamedKey::Space) => {
                            nav.handle(NavEvent::Push);
                        }
                        Key::Named(NamedKey::Escape) => elwt.exit(),
                        _ => {}
                    }
                    window.request_redraw();
                }

                WindowEvent::MouseWheel { delta, .. } => {
                    // Accumulate, so a trackpad's fine-grained scroll turns the
                    // dial at something close to one detent per notch rather
                    // than spinning it wildly.
                    pending_scroll += match delta {
                        MouseScrollDelta::LineDelta(_, y) => y,
                        MouseScrollDelta::PixelDelta(p) => p.y as f32 / 40.0,
                    };
                    let detents = pending_scroll.trunc();
                    if detents != 0.0 {
                        pending_scroll -= detents;
                        nav.handle(NavEvent::Turn(-detents as i32));
                        window.request_redraw();
                    }
                }

                WindowEvent::RedrawRequested => {
                    draw(&mut pixmap, &nav.frame(), &team);

                    let (Some(w), Some(h)) = (NonZeroU32::new(W), NonZeroU32::new(H)) else {
                        return;
                    };
                    if surface.resize(w, h).is_err() {
                        return;
                    }
                    let Ok(mut buffer) = surface.buffer_mut() else {
                        return;
                    };
                    // tiny-skia gives premultiplied RGBA; softbuffer wants 0RGB.
                    for (dst, px) in buffer.iter_mut().zip(pixmap.pixels()) {
                        let c = px.demultiply();
                        *dst = (u32::from(c.red()) << 16)
                            | (u32::from(c.green()) << 8)
                            | u32::from(c.blue());
                    }
                    let _ = buffer.present();
                }

                _ => {}
            },

            Event::NewEvents(_) => {
                // The clock lives here, in the host — never inside dial-nav.
                let now = Instant::now();
                let dt = now - last;
                if dt >= frame_time {
                    last = now;
                    let effects = nav.handle(NavEvent::Tick(dt));
                    if !effects.is_empty() {
                        for e in &effects {
                            println!("{e:?}");
                        }
                    }
                    window.request_redraw();
                }
            }

            _ => {}
        }
    })?;

    Ok(())
}

/// Render each state to a PNG, with no window and no display.
///
/// This is how the renderer gets checked on a build machine — and it is the
/// difference between "it compiled" and knowing what it actually draws.
fn write_shots(dir: &str, team: &Team) -> Result<(), Box<dyn std::error::Error>> {
    std::fs::create_dir_all(dir)?;
    let mut pixmap = Pixmap::new(W, H).ok_or("could not allocate the pixmap")?;

    /// A named state to render: its name, and how to get the panel into it.
    type Shot = (&'static str, fn() -> Nav);

    let shots: [Shot; 4] = [
        ("home", panel),
        ("home-focus-toggle", || {
            let mut nav = panel();
            nav.handle(NavEvent::Turn(2));
            nav.handle(NavEvent::Push); // the mic toggles on, stays home
            nav
        }),
        ("tile-open", || {
            let mut nav = panel();
            nav.handle(NavEvent::Push);
            nav.handle(NavEvent::Turn(4));
            nav
        }),
        ("tile-countdown", || {
            let mut nav = panel();
            nav.handle(NavEvent::Push);
            // Six seconds in: the line is a quarter left, and it reads
            // "HOME IN 2".
            nav.handle(NavEvent::Tick(Duration::from_millis(6_000)));
            nav
        }),
    ];

    for (name, build) in shots {
        let nav = build();
        draw(&mut pixmap, &nav.frame(), team);
        let path = format!("{dir}/{name}.png");
        pixmap.save_png(&path)?;
        println!("wrote {path}");
    }

    Ok(())
}

// ── Drawing ──────────────────────────────────────────────────────────────────

fn draw(pixmap: &mut Pixmap, frame: &Frame<'_>, team: &Team) {
    pixmap.fill(ink());

    match frame.screen {
        Screen::Home => draw_home(pixmap, frame, team),
        Screen::Tile { index } => draw_tile(pixmap, frame, team, index),
    }

    // The band light along the bottom edge: the team's colour as light.
    fill_rect(pixmap, 0.0, H as f32 - 4.0, W as f32, 4.0, team.light);

    let footer_scale = 2;
    text(
        pixmap,
        &format!("{} · ARROWS OR SCROLL TURN · ENTER PUSHES", team.name),
        24.0,
        H as f32 - 16.0 - font::text_height(footer_scale) as f32,
        footer_scale,
        dim(),
    );
}

fn draw_home(pixmap: &mut Pixmap, frame: &Frame<'_>, team: &Team) {
    grid(pixmap, team);
    text(pixmap, "DIAL PANEL", 24.0, 28.0, 3, dim());

    let n = frame.tiles.len().max(1);
    let gap = 24.0;
    let margin = 48.0;
    let total = W as f32 - margin * 2.0;
    let tile_w = (total - gap * (n as f32 - 1.0)) / n as f32;
    let tile_h = 300.0;
    let y = (H as f32 - tile_h) / 2.0;

    for (i, tile) in frame.tiles.iter().enumerate() {
        let x = margin + i as f32 * (tile_w + gap);
        let focused = i == frame.focus;

        fill_round(
            pixmap,
            RoundRect::new(x, y, tile_w, tile_h, 14.0),
            tile_bg(),
        );

        // Focus is a white ring and a caret. Never a colour — the xxx5 rule.
        if focused {
            stroke_round(
                pixmap,
                RoundRect::new(x, y, tile_w, tile_h, 14.0),
                3.0,
                white(),
            );
            caret(pixmap, x + tile_w / 2.0, y - 18.0, 11.0, white());
        }

        let label_scale = 2;
        text_centered(
            pixmap,
            &tile.label,
            x + tile_w / 2.0,
            y + 28.0,
            label_scale,
            if focused { white() } else { dim() },
        );

        let reading = value_text(tile, frame.values[i]);
        text_centered(
            pixmap,
            &reading,
            x + tile_w / 2.0,
            y + tile_h / 2.0 - 20.0,
            5,
            if focused { white() } else { dim() },
        );

        // A toggle that is on shows it as light, at the foot of the tile.
        if let (TileKind::Toggle, Value::OnOff(true)) = (&tile.kind, frame.values[i]) {
            fill_round(
                pixmap,
                RoundRect::new(x + 24.0, y + tile_h - 30.0, tile_w - 48.0, 6.0, 3.0),
                team.light,
            );
        }
    }
}

fn draw_tile(pixmap: &mut Pixmap, frame: &Frame<'_>, team: &Team, index: usize) {
    let tile = &frame.tiles[index];

    text_centered(pixmap, &tile.label, W as f32 / 2.0, 120.0, 4, dim());
    text_centered(
        pixmap,
        &value_text(tile, frame.values[index]),
        W as f32 / 2.0,
        H as f32 / 2.0 - 70.0,
        12,
        white(),
    );

    // A range tile shows where it sits between its ends.
    if let TileKind::Range { min, max, .. } = tile.kind {
        if let Value::Number(v) = frame.values[index] {
            let track_w = 700.0;
            let x = (W as f32 - track_w) / 2.0;
            let y = H as f32 / 2.0 + 90.0;
            fill_round(pixmap, RoundRect::new(x, y, track_w, 8.0, 4.0), tile_bg());

            let span = (max - min).max(1) as f32;
            let filled = ((v - min) as f32 / span).clamp(0.0, 1.0) * track_w;
            if filled > 0.0 {
                fill_round(pixmap, RoundRect::new(x, y, filled, 8.0, 4.0), team.light);
            }
        }
    }

    // The idle reset: a draining line, and the words.
    if let Some(idle) = frame.idle {
        let track_w = 360.0;
        let x = (W as f32 - track_w) / 2.0;
        let y = H as f32 - 96.0;

        // The track is drawn behind it, so what is draining is legible as
        // something draining rather than as a stub of a line.
        fill_round(pixmap, RoundRect::new(x, y, track_w, 4.0, 2.0), tile_bg());
        fill_round(
            pixmap,
            RoundRect::new(x, y, track_w * idle.progress, 4.0, 2.0),
            white(),
        );
        text_centered(
            pixmap,
            &format!("HOME IN {}", idle.remaining_secs),
            W as f32 / 2.0,
            y + 20.0,
            2,
            dim(),
        );
    }
}

/// The faint grid both teams sit on — warm for IGNITION, cyan for NIGHTFALL.
/// Barely there on purpose: it is the room's light, not a UI element.
fn grid(pixmap: &mut Pixmap, team: &Team) {
    let mut c = team.secondary;
    c.set_alpha(0.06);
    let spacing = 40.0;

    let mut x = 0.0;
    while x < W as f32 {
        fill_rect(pixmap, x, 0.0, 1.0, H as f32, c);
        x += spacing;
    }
    let mut y = 0.0;
    while y < H as f32 {
        fill_rect(pixmap, 0.0, y, W as f32, 1.0, c);
        y += spacing;
    }
}

fn value_text(tile: &Tile, value: Value) -> String {
    match (&tile.kind, value) {
        (TileKind::Range { unit, .. }, Value::Number(n)) => format!("{n}{unit}"),
        (TileKind::Toggle, Value::OnOff(on)) => (if on { "ON" } else { "OFF" }).to_string(),
        (TileKind::Action, _) => "PUSH".to_string(),
        (TileKind::Info, _) => "--".to_string(),
        _ => String::new(),
    }
}

// ── Primitives ───────────────────────────────────────────────────────────────

fn paint_of(color: Color) -> Paint<'static> {
    let mut paint = Paint::default();
    paint.set_color(color);
    paint.anti_alias = true;
    paint
}

fn fill_rect(pixmap: &mut Pixmap, x: f32, y: f32, w: f32, h: f32, color: Color) {
    if w <= 0.0 || h <= 0.0 {
        return;
    }
    if let Some(rect) = Rect::from_xywh(x, y, w, h) {
        pixmap.fill_rect(rect, &paint_of(color), Transform::identity(), None);
    }
}

/// A rounded rectangle, passed as one value so the drawing helpers do not each
/// take five loose floats.
#[derive(Clone, Copy)]
struct RoundRect {
    x: f32,
    y: f32,
    w: f32,
    h: f32,
    r: f32,
}

impl RoundRect {
    fn new(x: f32, y: f32, w: f32, h: f32, r: f32) -> Self {
        Self { x, y, w, h, r }
    }
}

fn round_rect_path(x: f32, y: f32, w: f32, h: f32, r: f32) -> Option<tiny_skia::Path> {
    if w <= 0.0 || h <= 0.0 {
        return None;
    }
    let r = r.min(w / 2.0).min(h / 2.0);
    let mut pb = PathBuilder::new();
    pb.move_to(x + r, y);
    pb.line_to(x + w - r, y);
    pb.quad_to(x + w, y, x + w, y + r);
    pb.line_to(x + w, y + h - r);
    pb.quad_to(x + w, y + h, x + w - r, y + h);
    pb.line_to(x + r, y + h);
    pb.quad_to(x, y + h, x, y + h - r);
    pb.line_to(x, y + r);
    pb.quad_to(x, y, x + r, y);
    pb.close();
    pb.finish()
}

fn fill_round(pixmap: &mut Pixmap, rect: RoundRect, color: Color) {
    if let Some(path) = round_rect_path(rect.x, rect.y, rect.w, rect.h, rect.r) {
        pixmap.fill_path(
            &path,
            &paint_of(color),
            FillRule::Winding,
            Transform::identity(),
            None,
        );
    }
}

fn stroke_round(pixmap: &mut Pixmap, rect: RoundRect, width: f32, color: Color) {
    if let Some(path) = round_rect_path(rect.x, rect.y, rect.w, rect.h, rect.r) {
        let stroke = Stroke {
            width,
            ..Stroke::default()
        };
        pixmap.stroke_path(
            &path,
            &paint_of(color),
            &stroke,
            Transform::identity(),
            None,
        );
    }
}

/// The focus caret: a small triangle pointing down at the focused tile.
fn caret(pixmap: &mut Pixmap, cx: f32, cy: f32, size: f32, color: Color) {
    let mut pb = PathBuilder::new();
    pb.move_to(cx - size, cy - size);
    pb.line_to(cx + size, cy - size);
    pb.line_to(cx, cy + size * 0.6);
    pb.close();
    if let Some(path) = pb.finish() {
        pixmap.fill_path(
            &path,
            &paint_of(color),
            FillRule::Winding,
            Transform::identity(),
            None,
        );
    }
}

fn text(pixmap: &mut Pixmap, s: &str, x: f32, y: f32, scale: usize, color: Color) {
    let tracking = scale.max(1);
    let mut pen = x;
    for c in s.chars() {
        let g = font::glyph(c);
        for (row, bits) in g.iter().enumerate() {
            for col in 0..font::GLYPH_W {
                if bits & (1 << (font::GLYPH_W - 1 - col)) != 0 {
                    fill_rect(
                        pixmap,
                        pen + (col * scale) as f32,
                        y + (row * scale) as f32,
                        scale as f32,
                        scale as f32,
                        color,
                    );
                }
            }
        }
        pen += (font::GLYPH_W * scale + tracking) as f32;
    }
}

fn text_centered(pixmap: &mut Pixmap, s: &str, cx: f32, y: f32, scale: usize, color: Color) {
    let w = font::text_width(s, scale, scale.max(1)) as f32;
    text(pixmap, s, cx - w / 2.0, y, scale, color);
}
