# Racket Tracker

A lightweight Android app for keeping track of tennis rackets and their maintenance history.

Racket Tracker lets you manage multiple physical rackets, see their current strings and grips at a glance, and keep a simple history of equipment changes. All data is stored locally on the device — no account, backend, or cloud connection is required.

## Features

- Track multiple rackets and the setups - grips, strings etc.
- Record string changes with gauge, tension, date, and notes
- Record grip changes with color, date, and notes
- Keep track of the setup of your current match racket
- Browse string and grip changes in a combined history

## Setup

Requires Python 3.13+.

```bash
git clone https://github.com/adampirog/racket-tracker.git
cd racket-tracker
```

Install the project together with the Flet development/build tooling:

```bash
pip install -e .
```

## Run locally

To start with demo data:

```bash
RACKET_TRACKER_DEMO_DATA=1 flet run -r main.py
```

## Build for Android

Flet requires JDK 17 and the Android SDK for Android builds. If compatible installations are not available,
Flet can set them up during the first build.

Build a release APK:

```bash
flet build apk
```

The generated APK is placed under:

```text
build/apk/
```
