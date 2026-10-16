# Racket Tracker

A lightweight Android app for keeping track of tennis rackets and their maintenance history.

Racket Tracker lets you manage multiple physical rackets, see their current strings and grips at a glance, and keep a simple history of equipment changes. All data is stored locally on the device — no account, backend, or cloud connection is required.

## Features

- Track multiple rackets, including duplicate models
- Choose a racket image from the built-in catalogue
- Record string changes with gauge, date, and notes
- Record grip changes with color, date, and notes
- See the current string and grip for each racket
- Browse string and grip changes in a combined history
- Local SQLite storage with no login or external service required

## Setup

Requires Python 3.13+.

```bash
git clone https://github.com/adampirog/racket-tracker.git
cd racket-tracker

python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install the project together with the Flet development/build tooling:

```bash
pip install -e .
```

## Run locally

To start with demo data:

```bash
RACKET_TRACKER_DEMO_DATA=1 flet run -r racket_tracker/main.py
```

On Windows PowerShell:

```powershell
$env:RACKET_TRACKER_DEMO_DATA="1"
flet run -r racket_tracker/main.py
```

## Build for Android

Flet requires JDK 17 and the Android SDK for Android builds. If compatible installations are not available, Flet can set them up during the first build.

Build a release APK:

```bash
flet build apk
```

The generated APK is placed under:

```text
build/apk/
```

For Google Play distribution, build an Android App Bundle instead:

```bash
flet build aab
```

The generated bundle is placed under:

```text
build/aab/
```

## Install on an Android device

Enable **Developer options** and **USB debugging** on the device, connect it over USB, and confirm that ADB can see it:

```bash
adb devices
```

Install the APK:

```bash
adb install build/apk/<racket-tracker.apk>
```

The update must use the same application ID and compatible signing key as the installed version.
