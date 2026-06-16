#!/bin/bash
echo ""
echo " =========================================="
echo "  ERP System — Philippine HR & Payroll"
echo " =========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo " ERROR: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Install dependencies
echo " Checking dependencies..."
pip3 install flask werkzeug openpyxl reportlab --quiet --exists-action i 2>/dev/null

# Run
if [ -z "$1" ]; then
    python3 run.py
else
    python3 run.py --client "$1"
fi
