import json
from pathlib import Path

import pytest

from src.engine import repository


@pytest.fixture()
def temp_data_dir(tmp_path):
    original = repository.DATA_DIR
    repository.DATA_DIR = tmp_path
    yield tmp_path
    repository.DATA_DIR = original


def test_create_update_delete_wrestler(temp_data_dir: Path):
    created = repository.create_wrestler({"name": "Hero", "persona": "Face"})
    assert created["name"] == "Hero"

    with pytest.raises(ValueError):
        repository.create_wrestler({"name": "Hero"})

    repository.update_wrestler("Hero", {"persona": "Heel", "finisher": "Smash"})
    updated_data = json.loads((temp_data_dir / "wrestlers.json").read_text())
    assert updated_data["wrestlers"][0]["persona"] == "Heel"
    assert updated_data["wrestlers"][0]["finisher"] == "Smash"

    repository.delete_wrestler("Hero")
    saved = json.loads((temp_data_dir / "wrestlers.json").read_text())
    assert saved["wrestlers"] == []

    with pytest.raises(ValueError):
        repository.delete_wrestler("Missing")


def test_assign_belt_requires_holder_exists(temp_data_dir: Path):
    repository.save_belts([{"name": "World Title", "current_holder": "", "prestige": 90}])
    with pytest.raises(ValueError):
        repository.assign_belt("World Title", "Unknown Wrestler")

    repository.create_wrestler({"name": "Champion"})
    assigned = repository.assign_belt("World Title", "Champion")
    assert assigned["current_holder"] == "Champion"


def test_delete_belt(temp_data_dir: Path):
    repository.save_belts(
        [
            {"name": "World Title", "current_holder": "Champion", "prestige": 90},
            {"name": "Tag Titles", "current_holder": "", "prestige": 80},
        ]
    )

    repository.delete_belt("World Title")
    saved = json.loads((temp_data_dir / "belts.json").read_text())
    assert saved["belts"] == [{"name": "Tag Titles", "current_holder": "", "prestige": 80}]

    with pytest.raises(ValueError):
        repository.delete_belt("Missing Belt")


def test_schedule_event_adds_entry(temp_data_dir: Path):
    event = {"name": "Monthly Mayhem", "date": "2024-10-01"}
    repository.schedule_event(event)

    saved = json.loads((temp_data_dir / "events.json").read_text())
    assert saved["events"][0]["name"] == "Monthly Mayhem"
