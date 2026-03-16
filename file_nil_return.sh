#!/bin/bash

# Example script to file a NIL return

echo "======================================"
echo "KRA NIL Return Filing System"
echo "======================================"
echo ""

# File a NIL return for PAYE (obligation code 7) for November 2024
# Using your PIN: A017174812E
python3 main.py file-nil \
    --pin A017174812E \
    --obligation 7 \
    --month 11 \
    --year 2024 \
    --confirm

echo ""
echo "======================================"
echo "Filing complete!"
echo "Check the 'acknowledgments' folder for the acknowledgment number."
echo "======================================" 