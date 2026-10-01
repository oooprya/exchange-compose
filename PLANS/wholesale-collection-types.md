Plan: Support collection (Инкассация/Подкрепление) flows

Goal
- Add add and collect operations that do not affect profit calculations or daily deals count; ensure they update balances correctly.

Steps
1. Update admin UI to allow collection types in exchange form (done).
2. Fix model field length to support 'add' and 'collect' (done).
3. Exclude collection types from profit aggregation and deal counts (done).
	- Modify `BalanceService.compute_global_totals` and `compute_node_stats` to ignore collection types when aggregating orders (done).
	- Adjust snapshot-based profit calculation to subtract the net effect of collection movements so they don't affect profit (done).
4. Add distinct badges/colors for collection types in admin list (done).
5. Fix profit calculation bugs (done):
	- Use correct movement_type values ("add"/"collect", not "add"/"collect").
	- Use shift.opened_at date instead of current date to find all collections.
	- Implement correct sign logic: add fully negates balance change from profit, collect partially negates.
6. Run `makemigrations` and `migrate`, run backend tests.

Notes
- After schema change, run migrations: `python manage.py makemigrations wholesale` and `python manage.py migrate`.
- Collection operations should update `CashBalance` and create `CashMovement` entries but must not modify `WholesaleOrder.profit` aggregation logic (profit stays 0 for collection types).
 - Collection operations should update `CashBalance` and create `CashMovement` entries but must not modify `WholesaleOrder.profit` aggregation logic (profit stays 0 for collection types).
 - Ensure reversal (сторно) of collection operations correctly reverts balances and logs a `reversal` movement.

Contact
- If anything unclear, ask before implementing further.
