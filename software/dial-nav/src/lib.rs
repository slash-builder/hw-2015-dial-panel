//! Dial Panel navigation — the interaction model, as pure logic.
//!
//! Turn to move focus. Push to open. Turn to adjust inside a tile. There is no
//! back button: you leave a tile by pushing, or by letting it time out and go
//! home on its own.
//!
//! This crate deliberately knows nothing about the device. It reads no GPIO, no
//! files and no clock — time arrives as [`Event::Tick`], input arrives as
//! [`Event::Turn`] and [`Event::Push`], and the result is a [`Frame`] a host
//! draws however it likes. That is what lets the same logic run under the
//! desktop harness and on the panel unchanged, and it is why the eight-second
//! idle reset can be unit-tested without waiting eight seconds.
//!
//! What this crate does *not* decide: colour. Focus is reported as an index and
//! a mode; the xxx5 rule that focus is a white ring and never a colour is the
//! renderer's to keep.

use std::time::Duration;

/// How long a tile stays open with no input before the panel goes home.
///
/// The concept sheet says "about 8 seconds". Whether this is adjustable, and by
/// whom, is an open question for `ux-engineer` and DJ — so it is a parameter
/// here rather than a constant, and nothing in this crate assumes the default.
pub const DEFAULT_IDLE_TIMEOUT: Duration = Duration::from_secs(8);

/// Tuning that a host may legitimately vary.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Config {
    /// Idle time before an open tile returns home.
    pub idle_timeout: Duration,
    /// Whether focus wraps past the ends of the tile row.
    ///
    /// A continuous rotary control has no end-stop to feel, so wrapping is the
    /// honest default: the dial never "hits a wall" that the hand cannot sense.
    pub wrap_focus: bool,
    /// Whether the idle reset also returns focus to the first tile.
    ///
    /// Default `false`: going home is about leaving a tile, not about forgetting
    /// where you were standing. **Open question** for `ux-engineer` — a wall
    /// panel that always greets you at the same tile is a defensible other
    /// answer, so this is a switch rather than a decision baked into the code.
    pub idle_resets_focus: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            idle_timeout: DEFAULT_IDLE_TIMEOUT,
            wrap_focus: true,
            idle_resets_focus: false,
        }
    }
}

/// What a tile does when you push it.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TileKind {
    /// Opens, and turning adjusts the value live — a dimmer, a volume, a setpoint.
    Range {
        min: i32,
        max: i32,
        /// Value change per detent of the dial.
        step: i32,
        /// Suffix a renderer may show after the number, e.g. "%" or "°".
        unit: String,
    },
    /// Flips on push. Does not open a screen — there is nothing to adjust.
    Toggle,
    /// Fires once on push. Does not open a screen.
    Action,
    /// Opens to be read. Turning does nothing; it goes home on push or on idle.
    Info,
}

/// One thing on the home screen.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Tile {
    /// Stable identifier for the host to map onto whatever it controls.
    pub id: String,
    /// Human label. Copy is `ux-engineer`'s; this crate only carries it.
    pub label: String,
    pub kind: TileKind,
}

impl Tile {
    pub fn range(id: &str, label: &str, min: i32, max: i32, step: i32, unit: &str) -> Self {
        Self {
            id: id.to_string(),
            label: label.to_string(),
            kind: TileKind::Range {
                min,
                max,
                step,
                unit: unit.to_string(),
            },
        }
    }

    pub fn toggle(id: &str, label: &str) -> Self {
        Self {
            id: id.to_string(),
            label: label.to_string(),
            kind: TileKind::Toggle,
        }
    }

    pub fn action(id: &str, label: &str) -> Self {
        Self {
            id: id.to_string(),
            label: label.to_string(),
            kind: TileKind::Action,
        }
    }

    pub fn info(id: &str, label: &str) -> Self {
        Self {
            id: id.to_string(),
            label: label.to_string(),
            kind: TileKind::Info,
        }
    }
}

/// A tile's current state.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Value {
    Number(i32),
    OnOff(bool),
    /// Actions and info tiles hold nothing.
    None,
}

impl Value {
    pub fn as_number(self) -> Option<i32> {
        match self {
            Value::Number(n) => Some(n),
            _ => None,
        }
    }

    pub fn as_on_off(self) -> Option<bool> {
        match self {
            Value::OnOff(b) => Some(b),
            _ => None,
        }
    }
}

/// Input, as the device produces it.
///
/// The rotary encoder is configured as a *relative* axis, so a turn arrives as a
/// signed count of detents rather than an absolute position. A fast spin can
/// deliver several at once, which is why [`Event::Turn`] carries a delta instead
/// of being a single-step "next"/"previous".
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Event {
    /// Detents turned; positive is clockwise.
    Turn(i32),
    /// The dial was pushed. On the device this arrives as `KEY_ENTER`.
    Push,
    /// Time passed. The host decides how often; accuracy of the countdown is
    /// bounded by how fine these are.
    Tick(Duration),
}

/// Which screen is showing.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Screen {
    Home,
    /// A tile is open. Only `Range` and `Info` tiles can be open — `Toggle` and
    /// `Action` do their work and stay home.
    Tile {
        index: usize,
    },
}

/// Why the panel went home.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HomeReason {
    /// The dial was pushed.
    Push,
    /// Nobody touched it for [`Config::idle_timeout`].
    Idle,
}

/// Something happened that the host may want to act on — light an LED, play a
/// tone, switch a relay.
///
/// Returned rather than performed, because this crate does not touch hardware.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Effect {
    FocusMoved {
        index: usize,
    },
    Opened {
        index: usize,
    },
    ValueChanged {
        index: usize,
        value: i32,
    },
    /// A range tile was turned but the value did not move, because it is already
    /// at its limit. Worth surfacing: it is the moment a device should feel like
    /// it hit an end-stop rather than feeling broken.
    ValueAtLimit {
        index: usize,
        value: i32,
    },
    Toggled {
        index: usize,
        on: bool,
    },
    ActionFired {
        index: usize,
    },
    WentHome {
        reason: HomeReason,
    },
}

/// The idle countdown, while one is running.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Idle {
    /// Time left before the panel goes home.
    pub remaining: Duration,
    /// Whole seconds to show. Counts 8, 7, … 1 and never displays 0 while the
    /// tile is still open — the concept's "HOME IN n", with the wording left to
    /// the renderer.
    pub remaining_secs: u32,
    /// 1.0 when the countdown starts, 0.0 as it expires. The draining line.
    pub progress: f32,
}

/// Everything a renderer needs for one frame.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Frame<'a> {
    pub screen: Screen,
    /// The focused tile on the home screen. Still meaningful while a tile is
    /// open — it is the tile you came from, and the one you return to.
    pub focus: usize,
    pub tiles: &'a [Tile],
    pub values: &'a [Value],
    /// `Some` only while a tile is open, because the home screen has nowhere to
    /// go home *to*.
    pub idle: Option<Idle>,
}

/// The navigation state machine.
#[derive(Debug, Clone)]
pub struct Nav {
    config: Config,
    tiles: Vec<Tile>,
    values: Vec<Value>,
    screen: Screen,
    focus: usize,
    /// Time since the last input, counted only while a tile is open.
    idle_elapsed: Duration,
}

impl Nav {
    /// Build a panel from its tiles. Values start at each tile's natural
    /// beginning: the low end of a range, off for a toggle.
    pub fn new(tiles: Vec<Tile>, config: Config) -> Self {
        let values = tiles
            .iter()
            .map(|t| match &t.kind {
                TileKind::Range { min, .. } => Value::Number(*min),
                TileKind::Toggle => Value::OnOff(false),
                TileKind::Action | TileKind::Info => Value::None,
            })
            .collect();

        Self {
            config,
            tiles,
            values,
            screen: Screen::Home,
            focus: 0,
            idle_elapsed: Duration::ZERO,
        }
    }

    /// Set a tile's starting value — for a host restoring state it already knows.
    ///
    /// Returns `false` if the index does not exist or the value does not suit the
    /// tile, rather than panicking on a host's bad restore.
    pub fn set_value(&mut self, index: usize, value: Value) -> bool {
        let Some(tile) = self.tiles.get(index) else {
            return false;
        };
        let ok = matches!(
            (&tile.kind, value),
            (TileKind::Range { .. }, Value::Number(_)) | (TileKind::Toggle, Value::OnOff(_))
        );
        if ok {
            if let Value::Number(n) = value {
                if let TileKind::Range { min, max, .. } = tile.kind {
                    self.values[index] = Value::Number(n.clamp(min, max));
                    return true;
                }
            }
            self.values[index] = value;
        }
        ok
    }

    pub fn screen(&self) -> Screen {
        self.screen
    }

    pub fn focus(&self) -> usize {
        self.focus
    }

    pub fn tiles(&self) -> &[Tile] {
        &self.tiles
    }

    pub fn value(&self, index: usize) -> Option<Value> {
        self.values.get(index).copied()
    }

    /// Feed one event in; get back whatever the host should act on.
    pub fn handle(&mut self, event: Event) -> Vec<Effect> {
        match event {
            Event::Tick(dt) => self.tick(dt),
            Event::Turn(delta) => {
                self.idle_elapsed = Duration::ZERO;
                self.turn(delta)
            }
            Event::Push => {
                self.idle_elapsed = Duration::ZERO;
                self.push()
            }
        }
    }

    /// The current frame.
    pub fn frame(&self) -> Frame<'_> {
        Frame {
            screen: self.screen,
            focus: self.focus,
            tiles: &self.tiles,
            values: &self.values,
            idle: self.idle(),
        }
    }

    fn idle(&self) -> Option<Idle> {
        if self.screen == Screen::Home {
            return None;
        }
        let timeout = self.config.idle_timeout;
        let remaining = timeout.saturating_sub(self.idle_elapsed);

        // Round up, so the countdown shows 8 for the whole of the first second
        // and only reaches 0 at the moment it actually goes home.
        let remaining_secs = {
            let nanos = remaining.subsec_nanos();
            remaining.as_secs() as u32 + u32::from(nanos > 0)
        };

        let progress = if timeout.is_zero() {
            0.0
        } else {
            (remaining.as_secs_f32() / timeout.as_secs_f32()).clamp(0.0, 1.0)
        };

        Some(Idle {
            remaining,
            remaining_secs,
            progress,
        })
    }

    fn tick(&mut self, dt: Duration) -> Vec<Effect> {
        // The home screen does not count down. There is nowhere to go.
        if self.screen == Screen::Home {
            return Vec::new();
        }

        self.idle_elapsed = self.idle_elapsed.saturating_add(dt);
        if self.idle_elapsed >= self.config.idle_timeout {
            self.go_home(HomeReason::Idle)
        } else {
            Vec::new()
        }
    }

    fn turn(&mut self, delta: i32) -> Vec<Effect> {
        if self.tiles.is_empty() || delta == 0 {
            return Vec::new();
        }

        match self.screen {
            Screen::Home => self.move_focus(delta),
            Screen::Tile { index } => self.adjust(index, delta),
        }
    }

    fn move_focus(&mut self, delta: i32) -> Vec<Effect> {
        let len = self.tiles.len() as i64;
        let next = if self.config.wrap_focus {
            (self.focus as i64 + delta as i64).rem_euclid(len)
        } else {
            (self.focus as i64 + delta as i64).clamp(0, len - 1)
        };
        let next = next as usize;

        if next == self.focus {
            return Vec::new();
        }
        self.focus = next;
        vec![Effect::FocusMoved { index: next }]
    }

    fn adjust(&mut self, index: usize, delta: i32) -> Vec<Effect> {
        let TileKind::Range { min, max, step, .. } = self.tiles[index].kind else {
            // Info tiles are read, not turned.
            return Vec::new();
        };

        let current = self.values[index].as_number().unwrap_or(min);
        // Saturating, so a violent spin on a wide range cannot overflow.
        let next = current
            .saturating_add(delta.saturating_mul(step))
            .clamp(min, max);

        if next == current {
            return vec![Effect::ValueAtLimit {
                index,
                value: current,
            }];
        }
        self.values[index] = Value::Number(next);
        vec![Effect::ValueChanged { index, value: next }]
    }

    fn push(&mut self) -> Vec<Effect> {
        if self.tiles.is_empty() {
            return Vec::new();
        }

        match self.screen {
            // Pushing inside a tile is the only deliberate way out. No back button.
            Screen::Tile { .. } => self.go_home(HomeReason::Push),
            Screen::Home => {
                let index = self.focus;
                match self.tiles[index].kind {
                    TileKind::Range { .. } | TileKind::Info => {
                        self.screen = Screen::Tile { index };
                        self.idle_elapsed = Duration::ZERO;
                        vec![Effect::Opened { index }]
                    }
                    TileKind::Toggle => {
                        let on = !self.values[index].as_on_off().unwrap_or(false);
                        self.values[index] = Value::OnOff(on);
                        vec![Effect::Toggled { index, on }]
                    }
                    TileKind::Action => vec![Effect::ActionFired { index }],
                }
            }
        }
    }

    fn go_home(&mut self, reason: HomeReason) -> Vec<Effect> {
        self.screen = Screen::Home;
        self.idle_elapsed = Duration::ZERO;
        if reason == HomeReason::Idle && self.config.idle_resets_focus {
            self.focus = 0;
        }
        vec![Effect::WentHome { reason }]
    }
}
