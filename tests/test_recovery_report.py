"""Check threshold crossings, matched windows, and report generation."""

import json

import numpy as np
import pytest

from aeolus_axisym.recovery_report import (
    below_intervals, main, markdown, summarize, window_summary, wind_series,
)


def run(times, winds, *, start=1800, off=900, version="cooling"):
    return {
        "meta": {"version": version, "t_start": start,
                 "params": {"cool_K": 30, "cool_on_s": off}},
        "history": [{"t_rel": t, "wind_max_sfc": w, "cool_J": 310e12}
                    for t, w in zip(times, winds)],
    }


def test_crossings_are_interpolated_and_separate_excursions_are_not_joined():
    t = np.array([0, 10, 20, 30, 40])
    wind = np.array([39, 19, 19, 39, 19])
    assert below_intervals(t, wind) == [[5.0, 25.0], [35.0, 40.0]]


def test_touching_threshold_splits_strictly_below_intervals():
    assert below_intervals([0, 10, 20], [19, 29, 19]) == [[0, 10], [10, 20]]
    assert below_intervals([0, 10], [29, 29]) == []


def test_below_average_does_not_imply_sustained_suppression():
    trial = run([0, 10, 20], [10, 40, 10])
    ctrl = run([0, 10, 20], [60, 60, 60])
    result = window_summary(trial, ctrl, 0, 20)
    assert result["mean_wind_m_s"] == 25
    assert result["max_wind_m_s"] == 40
    assert result["below_threshold_s"] == pytest.approx(2 * 19 / 3)
    assert result["below_threshold_fraction"] < 1
    assert result["noise_2sigma"] is None


def test_different_sampling_cadences_use_same_time_window():
    trial = run([0, 2, 10], [20, 22, 30])
    ctrl = run([0, 5, 10, 15], [40, 50, 60, 70])
    result = window_summary(trial, ctrl, 1, 9)
    assert result["mean_wind_m_s"] == 25
    assert result["control_mean_wind_m_s"] == 50
    assert result["change_vs_control"] == -0.5


@pytest.mark.parametrize("times,winds", [
    ([0], [20]), ([0, 0], [20, 20]), ([1, 0], [20, 20]),
    ([0, float("nan")], [20, 20]), ([0, 1], [20, float("inf")]),
])
def test_invalid_histories_are_rejected(times, winds):
    with pytest.raises(ValueError, match="finite, increasing"):
        wind_series(run(times, winds))


def test_incomplete_or_mismatched_controls_are_rejected():
    trial = run([0, 900, 1800], [50, 20, 20])
    with pytest.raises(ValueError, match="full intervention"):
        summarize(trial, run([0, 900], [60, 60]))
    with pytest.raises(ValueError, match="same simulation time"):
        summarize(trial, run([0, 900, 1800], [60, 60, 60], start=120))
    with pytest.raises(ValueError, match="fully covered"):
        window_summary(trial, trial, 0, 2700)


def test_partial_final_window_is_omitted_and_followup_is_censored():
    trial = run([0, 900, 1800, 2000], [50, 20, 20, 20])
    result = summarize(trial, run([0, 900, 1800, 2000], [60, 60, 60, 60]))
    assert len(result["windows"]) == 2
    assert result["post_cooling"]["longest_below_s"] == 1100
    assert result["liquid_air_Mt"] == 1
    assert "later recovery is unknown" in markdown([result])


def test_no_followup_and_zero_control_are_explicit():
    trial = run([0, 900], [20, 20])
    result = summarize(trial, run([0, 900], [0, 0]))
    assert result["post_cooling"] is None
    assert result["windows"][0]["change_vs_control"] is None
    assert "No post-cooling observation" in markdown([result])
    json.dumps(result, allow_nan=False)


def test_cli_writes_report_data_and_chart(tmp_path):
    directory = tmp_path / "runs"
    directory.mkdir()
    for name, winds in [("control", [60, 65, 60]), ("cooling", [50, 20, 20])]:
        data = run([0, 900, 1800], winds, version=name)
        if name == "control":
            data["meta"]["params"] = None
        (directory / f"{name}.json").write_text(json.dumps(data))
    dest = tmp_path / "report"
    main([str(tmp_path), "--version", "cooling", "--dest", str(dest)])
    assert json.loads((dest / "recovery_report.json").read_text())[0]["version"] == "cooling"
    assert "Cooling suppression" in (dest / "recovery_report.md").read_text()
    assert (dest / "recovery_timeseries.png").read_bytes().startswith(b"\x89PNG")
    with pytest.raises(SystemExit):
        main([str(tmp_path), "--version", "missing"])
