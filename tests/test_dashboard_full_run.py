import numpy as np
import pandas as pd

from dashboard_full_run import tactic_matrix_frame, write_parquet


def test_tactic_matrix_frame_rates():
    counts = np.array([[4, 0], [2, 3]])
    a_wins = np.array([[1, 0], [2, 1]])
    b_wins = np.array([[2, 0], [0, 1]])

    df = tactic_matrix_frame(counts, a_wins, b_wins, ["A", "B"])

    row = df[(df["a_tactic"] == "A") & (df["b_tactic"] == "A")].iloc[0]
    assert row["a_win_rate"] == 0.25
    assert row["b_win_rate"] == 0.5
    assert row["stalemate_rate"] == 0.25


def test_write_parquet_roundtrip(tmp_path):
    path = tmp_path / "data" / "sample.parquet"
    expected = pd.DataFrame([{"name": "alpha", "win_rate": 0.5}])

    write_parquet(expected, path)
    actual = pd.read_parquet(path)

    pd.testing.assert_frame_equal(actual, expected)
