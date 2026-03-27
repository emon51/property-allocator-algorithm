# PropertyAllocator

An algorithm that returns a **shuffled list of property sources** distributed among partners based on ratio, database availability, and a display limit.

---

## Overview

Given a set of partners with defined ratios, database availability, and a maximum display limit, `PropertyAllocator` calculates how many properties each partner should contribute to a final shuffled list.

It handles three real-world constraints automatically:
- Ratio-based allocation with ceiling rounding can exceed the limit → **reduction**
- A partner may have fewer properties in the database than allocated → **clamping + redistribution**
- The total available across all partners may be less than the limit → **output is capped**

---

## Usage

```python
from main import PropertyAllocator

ratio    = {"BC": 20, "V": 60, "EP": 20}
db_count = {"BC": 100, "V": 80, "EP": 50}
limit    = 24

allocator = PropertyAllocator(ratio, db_count, limit)
result    = allocator.show_property()

print(len(result))  # 24
print(result)       # ["V", "BC", "V", "EP", ...]
```

---

## API

### `PropertyAllocator(ratio, db_count, limit)`

| Parameter  | Type              | Description                                              |
|------------|-------------------|----------------------------------------------------------|
| `ratio`    | `dict[str, int]`  | Partner codes mapped to their percentage share (0–100)   |
| `db_count` | `dict[str, int]`  | Partner codes mapped to available property count in DB   |
| `limit`    | `int`             | Maximum number of properties to display (1–192)          |

### `show_property() -> list[str]`

Returns a shuffled list of partner codes with length:

```
len(result) = min(limit, sum(db_count.values()))
```

---

## Algorithm

### Step 1 — Allocate by Ratio

For each partner, compute the initial property count:

```
np = ceil(ratio * limit / 100)
```

### Step 2 — Build Priority List

Partners are ranked by `np` descending. Ties are broken alphabetically ascending. This order is used in all subsequent steps.

### Step 3 — Reduce to Limit

If `sum(np) > limit`, three passes run in order until the total is within limit:

1. **Pass 1** — Subtract `1` from the highest-priority partner with `np > 1`
2. **Pass 2** — Subtract `1` at a time from lowest-priority partners upward, skipping any with `np <= 1`
3. **Pass 3 (fallback)** — If still over limit, repeat Pass 2 but allow `np` to reach `0`

> A partner's `np` is never reduced to `0` in passes 1 or 2 as long as any alternative exists.

### Step 4 — Clamp to Database Availability

For each partner where `db_count < np`:

```
remaining_count += np - db_count
np = db_count
```

### Step 5 — Redistribute Remaining

`remaining_count` is redistributed to partners that still have capacity (`np < db_count`), cycling through the priority list and adding `1` per partner per pass until exhausted.

### Step 6 — Build & Shuffle

The final list is built by repeating each partner code `np` times, then shuffled randomly.

---

## Example Walkthrough

```
ratio    = {"BC": 20, "V": 60, "EP": 20}
db_count = {"BC": 100, "V": 80, "EP": 50}
limit    = 24
```

| Step | BC | V  | EP | Total |
|------|----|----|----|-------|
| Allocation (`ceil`) | 5 | 15 | 5 | 25 |
| Priority list | — | `["V", "BC", "EP"]` | — | — |
| Pass 1 reduction (V has highest priority, np > 1) | 5 | 14 | 5 | 24 ✓ |
| DB check (all within limits) | 5 | 14 | 5 | 24 |
| **Final** | **5** | **14** | **5** | **24** |

Output: a shuffled list of 24 partner codes.

---

## Constraints

| Parameter | Constraint |
|-----------|------------|
| `limit`   | `1 ≤ limit ≤ 192` |
| `ratio` values | Must sum to `100` |
| `db_count` values | Non-negative integers |

---

## Setup

**Requirements:** Python 3.10+

**1. Clone the repository**

```bash
git clone <repository-url>
cd <repository-folder>
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip3 install -r requirements.txt
```

Dependencies installed:

| Package    | Version  | Purpose                        |
|------------|----------|--------------------------------|
| `pytest`   | 9.0.2    | Test runner                    |
| `pluggy`   | 1.6.0    | Plugin system used by pytest   |
| `packaging`| 26.0     | Version parsing used by pytest |
| `iniconfig`| 2.3.0    | Config file parsing for pytest |
| `Pygments` | 2.19.2   | Syntax highlighting in output  |

---

## Running Tests

**Run all tests:**

```bash
pytest
```

**Run a specific test file:**

```bash
pytest test_main.py
```

**Run with verbose output:**

```bash
pytest test_main.py -v
```

**Run a specific test by name:**

```bash
pytest test_main.py -v -k "test_name"
```

---

## File Structure

```
.
├── main.py            # PropertyAllocator implementation
├── test_main.py       # Unit tests
├── requirements.txt   # Project dependencies
└── README.md
```
