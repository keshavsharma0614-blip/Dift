import subprocess
import sys


def test_schedule_cron_generates_default_expression():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "cron",
            "nightly-check",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "0 2 * * *" in result.stdout
    assert "dift profile run nightly-check" in result.stdout
    assert "--history" in result.stdout
    assert "--strict-exit-codes" in result.stdout


def test_schedule_cron_custom_time():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "cron",
            "nightly-check",
            "--hour",
            "5",
            "--minute",
            "30",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "30 5 * * *" in result.stdout


def test_schedule_cron_invalid_hour_returns_error():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "cron",
            "nightly-check",
            "--hour",
            "30",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3


def test_schedule_create_list_show_delete(tmp_path):
    schedules_file = tmp_path / "schedules.json"

    create_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "create",
            "daily-check",
            "--profile",
            "nightly-check",
            "--cron",
            "0 2 * * *",
            "--schedules-file",
            str(schedules_file),
        ],
        capture_output=True,
        text=True,
    )

    assert create_result.returncode == 0
    assert schedules_file.exists()

    list_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "list",
            "--schedules-file",
            str(schedules_file),
        ],
        capture_output=True,
        text=True,
    )

    assert list_result.returncode == 0
    assert "daily-check" in list_result.stdout
    assert "nightly-check" in list_result.stdout

    show_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "show",
            "daily-check",
            "--schedules-file",
            str(schedules_file),
        ],
        capture_output=True,
        text=True,
    )

    assert show_result.returncode == 0
    assert "nightly-check" in show_result.stdout
    assert "0 2 * * *" in show_result.stdout

    delete_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "delete",
            "daily-check",
            "--schedules-file",
            str(schedules_file),
        ],
        capture_output=True,
        text=True,
    )

    assert delete_result.returncode == 0

    list_after_delete = subprocess.run(
        [
            sys.executable,
            "-m",
            "dift.cli",
            "schedule",
            "list",
            "--schedules-file",
            str(schedules_file),
        ],
        capture_output=True,
        text=True,
    )

    assert list_after_delete.returncode == 0
    assert "No schedules found" in list_after_delete.stdout