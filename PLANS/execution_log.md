Execution log

2026-04-16  — Increased `order_type` length in `backend/wholesale/models.py` to 20 to allow 'add' and 'collect'.
2026-04-16  — Updated `backend/wholesale/admin.py` to allow collection types in exchange form.
2026-04-16  — Created plan: `PLANS/wholesale-collection-types.md`.
2026-04-16  — Implemented collection handlers:
- Updated `BalanceService.apply_order` to handle `add` / `collect` and create `CashMovement` entries.
- Updated `BalanceService.reverse_order` to reverse collection operations.
- Updated profit computation to exclude collection types from order aggregations and subtract collection movements effect when using morning/evening snapshots.
2026-04-16  — Added admin badges for collection types and allowed collection types in exchange form.

Execution log

2026-04-16  — Fixed critical profit calculation bugs:
- BUG 1: admin.get_shift_report() and views.build_unfold_table() used wrong movement types ("add"/"collect" instead of "add"/"collect").
- BUG 2: Used timezone.localdate() (current date) instead of shift.opened_at date, causing collections from earlier dates to be missed.
- BUG 3: Sign calculation was incorrect - add should fully negate profit increase, collect shouldn't be double-negated.
- FIX: Updated profit formula to correctly handle collections:
  - Profit = (evening - morning) - collection_effect
  - Where collection_effect = sum of (add amounts) - sum of (collect amounts) in UAH
- Files updated: admin.py, views.py
- Result: Подкрепление (add) on 20,000 UAH now correctly results in 0 profit (not -357,000).

Next steps:
- Run migrations: `python manage.py makemigrations wholesale && python manage.py migrate`
- Restart container and test: create Подкрепление operation and verify profit stays 0.
- Re-close shift and verify report shows correct profit.
