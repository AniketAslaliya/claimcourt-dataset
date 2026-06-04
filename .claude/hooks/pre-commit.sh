#!/bin/bash
# Pre-commit hook: validate dataset if claims.csv was regenerated

# Check if any generator files or config changed
CHANGED=$(git diff --cached --name-only | grep -E "(generators/|config\.py|generate_dataset\.py)")

if [ -n "$CHANGED" ]; then
    echo "Generator files changed. Running validation..."
    
    # Check if data/claims.csv exists
    if [ -f "data/claims.csv" ]; then
        python validators/stats_check.py data/claims.csv
        if [ $? -ne 0 ]; then
            echo ""
            echo "ERROR: Dataset validation failed."
            echo "Fix the issues above before committing."
            echo "Run: python generate_dataset.py && python validators/stats_check.py data/claims.csv"
            exit 1
        fi
    fi
fi

# Check config.py constraints
if git diff --cached --name-only | grep -q "config.py"; then
    echo "config.py changed. Verifying constraints..."
    
    # Check FRAUD_DISTRIBUTION sums to 1.0
    python -c "
from config import FRAUD_DISTRIBUTION, LANGUAGE_WEIGHTS
fd_sum = sum(FRAUD_DISTRIBUTION.values())
lw_sum = sum(LANGUAGE_WEIGHTS.values())
assert abs(fd_sum - 1.0) < 0.001, f'FRAUD_DISTRIBUTION sums to {fd_sum}, not 1.0'
assert abs(lw_sum - 1.0) < 0.001, f'LANGUAGE_WEIGHTS sums to {lw_sum}, not 1.0'
print('  [PASS] FRAUD_DISTRIBUTION sums to 1.0')
print('  [PASS] LANGUAGE_WEIGHTS sums to 1.0')
"
    if [ $? -ne 0 ]; then
        echo "ERROR: config.py constraint violation. Fix before committing."
        exit 1
    fi
fi

echo "Pre-commit checks passed."
