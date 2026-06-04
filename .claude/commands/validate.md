# /validate — Run full validation suite

Run the stats checker on the generated dataset and report results.

## Steps
1. Check that `data/claims.csv` exists
2. Run `python validators/stats_check.py data/claims.csv`
3. Report which checks passed/failed
4. If any failed, suggest specific fixes with file locations

## Output
Print the validation results and, if all pass, confirm safe to publish.
