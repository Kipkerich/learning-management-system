import pytest
from django.urls import reverse, resolve
from assignments import views

@pytest.mark.parametrize(
    "name,view,kwargs",
    [
        ("assignments", views.assignments_view, None),
        ("create_assignment", views.create_assignment, None),
        ("assignment_detail", views.assignment_detail, {"pk": 1}),
        ("take_assignment", views.take_assignment, {"pk": 1}),
        ("add_questions", views.add_questions, {"pk": 1}),
        ("view_submissions", views.view_submissions, {"pk": 1}),
        ("grade_submission", views.grade_submission, {"pk": 1, "student_id": 1}),
        ("publish_assignment", views.publish_assignment, {"pk": 1}),
    ],
)
def test_urls_resolve_to_correct_views(name, view, kwargs):
    if kwargs:
        url = reverse(name, kwargs=kwargs)
    else:
        url = reverse(name)
    match = resolve(url)
    # For function-based views, match.func is the function itself
    assert match.func == view
