import pytest
from django.urls import reverse

# Endpoints without pk
NO_PK = [
    ("assignments", None),
    ("create_assignment", None),
]

# Endpoints with pk / ids (use dummy ids; we are not asserting 200 here)
WITH_PK = [
    ("assignment_detail", {"pk": 1}),
    ("take_assignment", {"pk": 1}),
    ("add_questions", {"pk": 1}),
    ("view_submissions", {"pk": 1}),
    ("publish_assignment", {"pk": 1}),
    ("grade_submission", {"pk": 1, "student_id": 1}),
]

@pytest.mark.django_db
@pytest.mark.parametrize("name,kwargs", NO_PK + WITH_PK)
def test_get_endpoints_do_not_500_as_anonymous(client, name, kwargs):
    url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
    resp = client.get(url)
    # Accept anything except a server error. This keeps the test robust
    # until we add model fixtures and authentication.
    assert resp.status_code < 500
