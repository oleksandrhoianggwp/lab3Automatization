# Lab 3 — Selenium automation of OrangeHRM demo

One Selenium script that automates all three scenarios on
[opensource-demo.orangehrmlive.com](https://opensource-demo.orangehrmlive.com/web/index.php/auth/login).

## Setup

```bash
pip install -r requirements.txt
```

Selenium 4 ships with Selenium Manager which downloads the matching
ChromeDriver automatically — no extra setup needed (Chrome must be installed).

## Run

```bash
python main.py
```

The script logs in once and runs Part 1, Part 2, and Part 3 in order.
`part1.py`, `part2.py`, and `part3.py` are kept only as compatibility entry
points and run the same combined script.

## Layout

- [helpers.py](helpers.py) — driver factory, login, common waits, selectors
- [data/employees.json](data/employees.json) — list of 10 names to add in Part 2
- [main.py](main.py) — combined script for all task parts
