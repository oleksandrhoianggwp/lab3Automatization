# Lab 3 — Selenium automation of OrangeHRM demo

Three Selenium scripts that automate scenarios on
[opensource-demo.orangehrmlive.com](https://opensource-demo.orangehrmlive.com/web/index.php/auth/login).

## Setup

```bash
pip install -r requirements.txt
```

Selenium 4 ships with Selenium Manager which downloads the matching
ChromeDriver automatically — no extra setup needed (Chrome must be installed).

## Run

```bash
python part1.py    # Admin: prints Records Found + counts of Admin / ESS roles
python part2.py    # PIM:   adds 10 employees from data/employees.json
python part3.py    # PIM:   searches "Samuel", fills Contact Details
```

Run them in order — `part3.py` relies on the Samuel created by `part2.py`.

## Layout

- [helpers.py](helpers.py) — driver factory, login, common waits, selectors
- [data/employees.json](data/employees.json) — list of 10 names to add in Part 2
- [part1.py](part1.py) / [part2.py](part2.py) / [part3.py](part3.py) — scripts
