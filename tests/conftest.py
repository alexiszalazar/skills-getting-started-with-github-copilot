from copy import deepcopy

import pytest

from src.app import activities


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_state = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original_state)
