//! The interaction model, proved without a Pi.
//!
//! Every test here is the concept sheet's behaviour stated as an assertion:
//! turn to move, push to open, turn to adjust, no back button, home after ~8 s.

use std::time::Duration;

use dial_nav::{Config, Effect, Event, HomeReason, Nav, Screen, Tile, Value};

fn panel() -> Nav {
    Nav::new(
        vec![
            Tile::range("lamp", "Lamp", 0, 100, 5, "%"),
            Tile::toggle("mic", "Microphone"),
            Tile::action("scene", "Goodnight"),
            Tile::info("weather", "Outside"),
        ],
        Config::default(),
    )
}

fn feed(nav: &mut Nav, events: impl IntoIterator<Item = Event>) -> Vec<Effect> {
    events.into_iter().flat_map(|e| nav.handle(e)).collect()
}

// ── Turning on the home screen ───────────────────────────────────────────────

#[test]
fn turning_moves_focus() {
    let mut nav = panel();
    assert_eq!(nav.focus(), 0);

    assert_eq!(
        nav.handle(Event::Turn(1)),
        vec![Effect::FocusMoved { index: 1 }]
    );
    assert_eq!(nav.focus(), 1);

    nav.handle(Event::Turn(-1));
    assert_eq!(nav.focus(), 0);
}

#[test]
fn a_fast_spin_moves_by_its_whole_delta() {
    // The encoder is a relative axis; several detents can arrive at once.
    let mut nav = panel();
    nav.handle(Event::Turn(3));
    assert_eq!(nav.focus(), 3);
}

#[test]
fn focus_wraps_by_default() {
    // A continuous dial has no end-stop to feel, so it should not hit a wall.
    let mut nav = panel();
    nav.handle(Event::Turn(-1));
    assert_eq!(
        nav.focus(),
        3,
        "turning back from the first tile reaches the last"
    );

    nav.handle(Event::Turn(1));
    assert_eq!(
        nav.focus(),
        0,
        "and forward from the last returns to the first"
    );
}

#[test]
fn focus_clamps_when_wrapping_is_off() {
    let mut nav = Nav::new(
        vec![Tile::toggle("a", "A"), Tile::toggle("b", "B")],
        Config {
            wrap_focus: false,
            ..Config::default()
        },
    );
    nav.handle(Event::Turn(-5));
    assert_eq!(nav.focus(), 0);
    nav.handle(Event::Turn(50));
    assert_eq!(nav.focus(), 1);
}

#[test]
fn a_turn_that_changes_nothing_reports_nothing() {
    let mut nav = Nav::new(
        vec![Tile::toggle("only", "Only")],
        Config {
            wrap_focus: false,
            ..Config::default()
        },
    );
    assert!(nav.handle(Event::Turn(1)).is_empty());
}

// ── Pushing ──────────────────────────────────────────────────────────────────

#[test]
fn pushing_opens_a_range_tile() {
    let mut nav = panel();
    assert_eq!(nav.handle(Event::Push), vec![Effect::Opened { index: 0 }]);
    assert_eq!(nav.screen(), Screen::Tile { index: 0 });
}

#[test]
fn a_toggle_flips_without_leaving_home() {
    let mut nav = panel();
    nav.handle(Event::Turn(1)); // focus the microphone

    assert_eq!(
        nav.handle(Event::Push),
        vec![Effect::Toggled { index: 1, on: true }]
    );
    assert_eq!(nav.screen(), Screen::Home, "a toggle has nothing to open");
    assert_eq!(nav.value(1), Some(Value::OnOff(true)));

    nav.handle(Event::Push);
    assert_eq!(nav.value(1), Some(Value::OnOff(false)));
}

#[test]
fn an_action_fires_without_leaving_home() {
    let mut nav = panel();
    nav.handle(Event::Turn(2));

    assert_eq!(
        nav.handle(Event::Push),
        vec![Effect::ActionFired { index: 2 }]
    );
    assert_eq!(nav.screen(), Screen::Home);
}

// ── Adjusting inside a tile ──────────────────────────────────────────────────

#[test]
fn turning_inside_a_range_tile_adjusts_it_live() {
    let mut nav = panel();
    nav.handle(Event::Push);

    assert_eq!(
        nav.handle(Event::Turn(2)),
        vec![Effect::ValueChanged {
            index: 0,
            value: 10
        }],
        "two detents at a step of 5"
    );
    assert_eq!(nav.value(0), Some(Value::Number(10)));
    assert_eq!(nav.focus(), 0, "adjusting must not move focus");
}

#[test]
fn a_range_stops_at_its_limits_and_says_so() {
    let mut nav = panel();
    nav.handle(Event::Push);
    nav.handle(Event::Turn(1000));
    assert_eq!(nav.value(0), Some(Value::Number(100)));

    assert_eq!(
        nav.handle(Event::Turn(1)),
        vec![Effect::ValueAtLimit {
            index: 0,
            value: 100
        }],
        "the host needs this to make the dial feel like it hit an end-stop"
    );
}

#[test]
fn a_violent_spin_cannot_overflow() {
    let mut nav = Nav::new(
        vec![Tile::range(
            "wide",
            "Wide",
            i32::MIN,
            i32::MAX,
            1_000_000,
            "",
        )],
        Config::default(),
    );
    nav.handle(Event::Push);
    nav.handle(Event::Turn(i32::MAX));
    nav.handle(Event::Turn(i32::MIN));
    // Reaching here without panicking is the assertion.
    assert!(nav.value(0).and_then(Value::as_number).is_some());
}

#[test]
fn turning_an_info_tile_does_nothing() {
    let mut nav = panel();
    nav.handle(Event::Turn(3));
    nav.handle(Event::Push);
    assert_eq!(nav.screen(), Screen::Tile { index: 3 });
    assert!(nav.handle(Event::Turn(5)).is_empty());
}

// ── No back button ───────────────────────────────────────────────────────────

#[test]
fn pushing_is_the_only_deliberate_way_out_and_it_goes_all_the_way_home() {
    let mut nav = panel();
    nav.handle(Event::Push);
    nav.handle(Event::Turn(3));

    assert_eq!(
        nav.handle(Event::Push),
        vec![Effect::WentHome {
            reason: HomeReason::Push
        }]
    );
    assert_eq!(
        nav.screen(),
        Screen::Home,
        "there is no intermediate level to land on"
    );
    assert_eq!(
        nav.value(0),
        Some(Value::Number(15)),
        "leaving keeps what you set; adjustment is live, not a dialog to confirm"
    );
}

// ── The idle reset ───────────────────────────────────────────────────────────

#[test]
fn an_open_tile_goes_home_after_the_timeout_and_not_before() {
    let mut nav = panel();
    nav.handle(Event::Push);

    let early = feed(&mut nav, [Event::Tick(Duration::from_millis(7_999))]);
    assert!(early.is_empty(), "still open at 7.999 s");
    assert_eq!(nav.screen(), Screen::Tile { index: 0 });

    let late = nav.handle(Event::Tick(Duration::from_millis(1)));
    assert_eq!(
        late,
        vec![Effect::WentHome {
            reason: HomeReason::Idle
        }]
    );
    assert_eq!(nav.screen(), Screen::Home);
}

#[test]
fn the_home_screen_never_counts_down() {
    let mut nav = panel();
    let effects = feed(&mut nav, [Event::Tick(Duration::from_secs(600))]);
    assert!(effects.is_empty(), "home has nowhere to go home to");
    assert_eq!(nav.screen(), Screen::Home);
    assert!(nav.frame().idle.is_none());
}

#[test]
fn any_input_restarts_the_countdown() {
    let mut nav = panel();
    nav.handle(Event::Push);

    nav.handle(Event::Tick(Duration::from_secs(7)));
    nav.handle(Event::Turn(1)); // a hand on the dial
    let effects = feed(&mut nav, [Event::Tick(Duration::from_secs(7))]);

    assert!(
        effects.is_empty(),
        "the clock restarted when the dial moved"
    );
    assert_eq!(nav.screen(), Screen::Tile { index: 0 });
}

#[test]
fn the_countdown_reads_eight_down_to_one_and_drains_evenly() {
    let mut nav = panel();
    nav.handle(Event::Push);

    let idle = nav
        .frame()
        .idle
        .expect("a countdown runs while a tile is open");
    assert_eq!(idle.remaining_secs, 8, "it opens showing the full eight");
    assert!((idle.progress - 1.0).abs() < f32::EPSILON);

    nav.handle(Event::Tick(Duration::from_secs(4)));
    let idle = nav.frame().idle.unwrap();
    assert_eq!(idle.remaining_secs, 4);
    assert!(
        (idle.progress - 0.5).abs() < 0.001,
        "the draining line is half gone at half time"
    );

    // Rounds up, so "HOME IN 1" shows for the whole last second rather than
    // sitting on 0 while the tile is still open.
    nav.handle(Event::Tick(Duration::from_millis(3_500)));
    assert_eq!(nav.frame().idle.unwrap().remaining_secs, 1);
}

#[test]
fn going_home_keeps_your_place_by_default() {
    let mut nav = panel();
    nav.handle(Event::Turn(3));
    nav.handle(Event::Push);
    nav.handle(Event::Tick(Duration::from_secs(8)));

    assert_eq!(nav.screen(), Screen::Home);
    assert_eq!(
        nav.focus(),
        3,
        "leaving a tile is not forgetting where you stood"
    );
}

#[test]
fn going_home_can_reset_focus_when_a_host_asks_for_it() {
    let mut nav = Nav::new(
        panel().tiles().to_vec(),
        Config {
            idle_resets_focus: true,
            ..Config::default()
        },
    );
    nav.handle(Event::Turn(3));
    nav.handle(Event::Push);
    nav.handle(Event::Tick(Duration::from_secs(8)));
    assert_eq!(nav.focus(), 0);

    // Pushing out is a deliberate act, so it keeps your place either way.
    nav.handle(Event::Turn(2));
    nav.handle(Event::Push);
    nav.handle(Event::Push);
    assert_eq!(nav.focus(), 2);
}

#[test]
fn a_coarse_tick_still_goes_home_exactly_once() {
    // A host that ticks once a second, or once a minute, must not fire twice.
    let mut nav = panel();
    nav.handle(Event::Push);
    let effects = feed(
        &mut nav,
        [
            Event::Tick(Duration::from_secs(60)),
            Event::Tick(Duration::from_secs(60)),
        ],
    );
    assert_eq!(
        effects,
        vec![Effect::WentHome {
            reason: HomeReason::Idle
        }]
    );
}

// ── Hosts behaving badly ─────────────────────────────────────────────────────

#[test]
fn an_empty_panel_does_not_panic() {
    let mut nav = Nav::new(Vec::new(), Config::default());
    assert!(nav.handle(Event::Turn(3)).is_empty());
    assert!(nav.handle(Event::Push).is_empty());
    assert!(nav.handle(Event::Tick(Duration::from_secs(30))).is_empty());
    assert_eq!(nav.screen(), Screen::Home);
}

#[test]
fn restoring_a_value_clamps_and_refuses_nonsense() {
    let mut nav = panel();

    assert!(nav.set_value(0, Value::Number(250)));
    assert_eq!(
        nav.value(0),
        Some(Value::Number(100)),
        "clamped to the tile's max"
    );

    assert!(
        !nav.set_value(0, Value::OnOff(true)),
        "a range is not a toggle"
    );
    assert!(!nav.set_value(99, Value::Number(1)), "no such tile");
    assert_eq!(
        nav.value(0),
        Some(Value::Number(100)),
        "a refused restore changes nothing"
    );
}

#[test]
fn a_zero_length_timeout_goes_home_on_the_first_tick() {
    let mut nav = Nav::new(
        panel().tiles().to_vec(),
        Config {
            idle_timeout: Duration::ZERO,
            ..Config::default()
        },
    );
    nav.handle(Event::Push);
    assert_eq!(
        nav.handle(Event::Tick(Duration::from_millis(1))),
        vec![Effect::WentHome {
            reason: HomeReason::Idle
        }]
    );
}
