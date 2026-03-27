# Algorithm Design Problem

## Problem: Display Properties Based on Partner Ratio and Limit

We need to design an algorithm that returns a **shuffled list of
property sources** based on a given **ratio distribution**, **database
availability**, and a **maximum display limit**.

The function should distribute properties among partners proportionally
according to their ratio while respecting database availability and the
given limit.

---

## Function Signature
```python
def show_property(ratio: dict[str, int], db_count: dict[str, int], limit: int) -> list[str]:
    pass
```

---

## Requirements

### 1. Output

Return a **shuffled list of partner codes** representing properties to
display. The size of the list must not exceed `limit` and must not
exceed the total available properties across all partners.

    size = min(limit, sum(db_count.values()))

Example output:

    ["V", "BC", "EP", "V", "BC", "EP"]

---

### 2. Priority Order

Partners are ranked by their assigned property count (descending).
Ties are broken alphabetically (ascending) by partner name.

This priority order is used in reduction and redistribution steps.

---

### 3. Property Allocation by Ratio

For each partner, calculate the number of properties to assign:

    np = ceil(ratio_of_partner * limit / 100)

> Note: A partner's `np` must never be reduced to `0` if their ratio
> is greater than `0`. The minimum is `1`.

---

### 4. Total Property Check

    tp = sum(np for all partners)

If `tp > limit`, reduce allocations in two passes:

**Pass 1:** Subtract `1` from the partner with the **highest priority**
(largest np, alphabetically first on ties) that has `np > 1`.

**Pass 2:** If still over limit, subtract `1` at a time from partners
in **reverse priority order** (lowest first), skipping any partner
where `np <= 1`, until `tp == limit`.

**Fallback (Pass 3):** If still over limit after both passes (all
partners are at `1`), repeat reverse-priority reduction but now allow
`np` to go down to `0`.

---

### 5. Database Availability Check

Each partner has a limited number of properties available in the
database (`dc`).

If `dc < np` for any partner:

    remaining_count += np - dc
    np = dc

Collect the total `remaining_count` from all such partners.

---

### 6. Redistribution of Remaining Count

Distribute `remaining_count` back to partners that still have capacity
(`np < dc`), going through the priority list repeatedly until either
`remaining_count` is exhausted or no partner has remaining capacity.

Each pass through the priority list adds `1` to the first eligible
partner before moving to the next.

---

## Constraints

    1 <= limit <= 192

---

## Example Input

### Ratio
```python
ratio = {"BC": 20, "V": 60, "EP": 20}
```

### Database Count
```python
db_count = {"BC": 100, "V": 80, "EP": 50}
```

### Limit
```python
limit = 24
```

---

## Example Walkthrough

**Step 1 — Allocation:**
- BC: ceil(20 * 24 / 100) = ceil(4.8) = 5
- V:  ceil(60 * 24 / 100) = ceil(14.4) = 15
- EP: ceil(20 * 24 / 100) = ceil(4.8) = 5

**Step 2 — Priority list** (by np desc, name asc):
`["V", "BC", "EP"]`

**Step 3 — Total check:**
tp = 5 + 15 + 5 = 25 > 24

- Pass 1: Reduce V (highest priority, np=15 > 1) → V=14, tp=24 ✓

**Step 4 — DB check:**
All partners have dc > np, so remaining_count = 0.

**Step 5 — Result:**
Build list of 24 items and shuffle.