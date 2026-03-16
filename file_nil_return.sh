#!/bin/bash

# Example script to file a NIL return

echo "======================================"
echo "KRA NIL Return Filing System"
echo "======================================"
echo ""

# Get current year (defaults to 2025 if not set)
CURRENT_YEAR=${1:-2025}
# Month 11 = November (hardcoded as per your original script)
CURRENT_MONTH=11

# File a NIL return for PAYE (obligation code 7) for November 2025
# Using your PIN: A017174812E
python3 main.py file-nil \
    --pin A017174812E \
    --obligation 7 \
    --month $CURRENT_MONTH \
    --year $CURRENT_YEAR \
    --confirm

echo ""
echo "======================================"
echo "Filing complete!"
echo "Check the 'acknowledgments' folder for the acknowledgment number."
echo "======================================" 