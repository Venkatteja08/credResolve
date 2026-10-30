import json
import sqlite3
import pandas as pd
import numpy as np
import io
import sys
import contextlib

with open("notebook/collections_deep_dive_analysis.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Global namespace for execution
exec_env = {
    "sqlite3": sqlite3,
    "pd": pd,
    "np": np
}

cell_idx = 1
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        code = "".join(cell["source"])
        stdout_buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stdout_buf):
                exec(code, exec_env)
            output_text = stdout_buf.getvalue()
            cell["execution_count"] = cell_idx
            cell["outputs"] = [{
                "name": "stdout",
                "output_type": "stream",
                "text": output_text.splitlines(keepends=True)
            }]
            print(f"Executed cell {cell_idx} successfully.")
        except Exception as e:
            err_msg = f"Error: {str(e)}\n" + stdout_buf.getvalue()
            cell["execution_count"] = cell_idx
            cell["outputs"] = [{
                "name": "stderr",
                "output_type": "stream",
                "text": err_msg.splitlines(keepends=True)
            }]
            print(f"Error executing cell {cell_idx}: {e}")
        cell_idx += 1

with open("notebook/collections_deep_dive_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)

print("\nNotebook execution and output population completed!")

