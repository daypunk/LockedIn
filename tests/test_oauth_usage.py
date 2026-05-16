"""Tests for the Anthropic OAuth utilization reader."""

from __future__ import annotations

import json

import pytest

import lockedin.hud.oauth_usage as ou


@pytest.fixture
def isolated_cache(tmp_path, monkeypatch):
    """Redirect cache_dir to tmp_path so tests don't touch the user's home."""
    cache_root = tmp_path / "cache"
    monkeypatch.setattr(ou, "_cache_dir", lambda: cache_root)
    return cache_root


@pytest.fixture
def isolated_creds(tmp_path, monkeypatch):
    """Redirect filesystem credential path to tmp_path."""
    creds_dir = tmp_path / "claude"
    creds_dir.mkdir()
    creds_path = creds_dir / ".credentials.json"
    monkeypatch.setattr(ou, "_credentials_path_filesystem", lambda: creds_path)
    return creds_path


def test_normalize_payload_handles_float_percent():
    """API returns utilization as a percentage; floats too (8.0 == 8%)."""
    raw = {"five_hour": {"utilization": 8.0}, "seven_day": {"utilization": 1.0}}
    out = ou._normalize_payload(raw)
    assert out["five_hour"] == 0.08
    assert out["seven_day"] == 0.01
    # No reset timestamps in this raw input, so the corresponding fields
    # are present but None.
    assert out["five_hour_resets_at"] is None
    assert out["seven_day_resets_at"] is None


def test_normalize_payload_handles_int_percent():
    raw = {"five_hour": {"utilization": 27}, "seven_day": {"utilization": 42}}
    out = ou._normalize_payload(raw)
    assert out["five_hour"] == 0.27
    assert out["seven_day"] == 0.42


def test_normalize_payload_handles_camelcase():
    raw = {"fiveHour": {"utilization": 50}, "sevenDay": {"utilization": 60}}
    out = ou._normalize_payload(raw)
    assert out["five_hour"] == 0.5
    assert out["seven_day"] == 0.6


def test_normalize_payload_low_percent_not_confused_with_fraction():
    """Regression guard: the old heuristic (`v / 100 if v > 1.5 else v`)
    misread sub-1.5% values (1.0 == 1%) as 100% fractions. The API always
    returns percentages, so it must be divided by 100 every time."""
    payload = ou._normalize_payload({
        "five_hour": {"utilization": 1.0, "resets_at": "2026-01-01T00:00:00Z"},
        "seven_day": {"utilization": 0.5, "resets_at": "2026-01-07T00:00:00Z"},
    })
    assert payload is not None
    assert payload["five_hour"] == 0.01
    assert payload["seven_day"] == 0.005

    zero = ou._normalize_payload({
        "five_hour": {"utilization": 0.0, "resets_at": "2026-01-01T00:00:00Z"},
        "seven_day": {"utilization": 0.0, "resets_at": "2026-01-07T00:00:00Z"},
    })
    assert zero is not None
    assert zero["five_hour"] == 0.0
    assert zero["seven_day"] == 0.0


def test_normalize_payload_extracts_reset_timestamps():
    raw = {
        "five_hour": {
            "utilization": 0.45,
            "resets_at": "2026-05-09T18:30:00Z",
        },
        "seven_day": {
            "utilization": 0.33,
            "resets_at": "2026-05-13T13:59:59Z",
        },
    }
    out = ou._normalize_payload(raw)
    assert out["five_hour_resets_at"] == "2026-05-09T18:30:00Z"
    assert out["seven_day_resets_at"] == "2026-05-13T13:59:59Z"


def test_normalize_payload_returns_none_when_keys_missing():
    assert ou._normalize_payload({}) is None
    assert ou._normalize_payload({"random": 1}) is None


def test_extract_access_token_handles_oauth_blob():
    creds = {"claudeAiOauth": {"accessToken": "tok123"}}
    assert ou._extract_access_token(creds) == "tok123"


def test_extract_access_token_handles_flat_blob():
    assert ou._extract_access_token({"access_token": "xyz"}) == "xyz"
    assert ou._extract_access_token({"accessToken": "abc"}) == "abc"


def test_extract_access_token_returns_none_when_absent():
    assert ou._extract_access_token({}) is None
    assert ou._extract_access_token({"claudeAiOauth": {}}) is None


def test_get_usage_returns_none_when_no_credentials(
    monkeypatch, tmp_path, isolated_cache, isolated_creds
):
    # No credentials file, no Keychain. Should return None silently.
    monkeypatch.setattr(ou, "_read_credentials_keychain_macos", lambda: None)
    assert ou.get_usage() is None


def test_get_usage_uses_cache_when_fresh(monkeypatch, isolated_cache):
    isolated_cache.mkdir(parents=True, exist_ok=True)
    cache_path = isolated_cache / "usage.json"
    cache_path.write_text(
        json.dumps(
            {"ts": 9999999999, "payload": {"five_hour": 0.5, "seven_day": 0.6}}
        ),
        encoding="utf-8",
    )

    # Fail loudly if any network or credential code runs.
    def _boom(*_args, **_kwargs):
        raise AssertionError("should hit cache, not credentials/network")

    monkeypatch.setattr(ou, "_read_credentials", _boom)
    out = ou.get_usage()
    assert out == {"five_hour": 0.5, "seven_day": 0.6}


def test_get_usage_succeeds_when_credentials_and_fetch_work(
    monkeypatch, isolated_cache, isolated_creds
):
    isolated_creds.write_text(
        json.dumps({"claudeAiOauth": {"accessToken": "valid"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(ou, "_read_credentials_keychain_macos", lambda: None)
    monkeypatch.setattr(
        ou,
        "_fetch_usage",
        lambda token: {"five_hour": {"utilization": 18.0}, "seven_day": {"utilization": 24.0}},
    )
    out = ou.get_usage()
    assert out["five_hour"] == 0.18
    assert out["seven_day"] == 0.24
    # Cache should have been written.
    assert (isolated_cache / "usage.json").exists()


def test_get_usage_returns_none_when_fetch_fails(
    monkeypatch, isolated_cache, isolated_creds
):
    isolated_creds.write_text(
        json.dumps({"claudeAiOauth": {"accessToken": "valid"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(ou, "_read_credentials_keychain_macos", lambda: None)
    monkeypatch.setattr(ou, "_fetch_usage", lambda token: None)
    assert ou.get_usage() is None


def test_get_usage_returns_none_when_token_missing(
    monkeypatch, isolated_cache, isolated_creds
):
    isolated_creds.write_text(json.dumps({"empty": True}), encoding="utf-8")
    monkeypatch.setattr(ou, "_read_credentials_keychain_macos", lambda: None)
    assert ou.get_usage() is None
