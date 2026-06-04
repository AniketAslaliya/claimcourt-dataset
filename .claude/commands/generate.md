# /generate — Generate dataset

Generate the IndiaClaimGuard dataset in sample or full mode.

## Arguments
- `--full` or `full`: Generate 100K rows (3-5 min)
- (no argument): Generate 500 rows (sample, ~10 sec)

## Steps
1. Run `python generate_dataset.py` (or with `--full`)
2. Display the generation summary
3. Automatically run `python validators/stats_check.py data/claims.csv`
4. Report results

## Output
Print generation summary and validation results.
