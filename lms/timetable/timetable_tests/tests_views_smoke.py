import pytest
from django.urls import reverse

NO_PK = [
    ("timetable", None),
    ("create_timetable", None),
    ("timetable_json", None),
]

WITH_PK = [
    ("edit_timetable", {"pk": 1}),
    ("delete_timetable", {"pk": 1}),
]

@pytest.mark.django_db
@pytest.mark.parametrize("name,kwargs", NO_PK + WITH_PK)
def test_get_endpoints_do_not_500_as_anonymous(client, name, kwargs):
    url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
    resp = client.get(url)
    # For now we only care that the view doesn’t crash (no 500s)
    assert resp.status_code < 500
