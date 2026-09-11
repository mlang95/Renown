#!/usr/bin/env python3
"""RETIRED — renown_data.py is now the hand-edited master for the node graph.

The original gen_nodes.py imported specs.csv + nodes_escalation.csv INTO
renown_data. That direction is dead: NODES (including 'escalation' and
'engine' fields) is edited directly in renown_data.py.

For spreadsheet views, run export_csvs.py (renown_data -> CSVs).
This guard exists so a stale notebook can't silently overwrite hand edits.
"""
import sys
sys.exit("gen_nodes.py is retired: edit renown_data.NODES directly; "
         "run export_csvs.py for CSV views.")
