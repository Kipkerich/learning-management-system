import pytest
from django.urls import reverse, resolve
from timetable import views

@pytest.mark.parametrize(
    "name,view,kwargs",
    [
        ("timetable", views.timetable_view, None),
        ("create_timetable", views.create_timetable, None),
        ("edit_timetable", views.edit_timetable, {"pk": 1}),
        ("delete_timetable", views.delete_timetable, {"pk": 1}),
        ("timetable_json", views.timetable_json, None),
    ],
)
def test_urls_resolve_to_correct_views(name, view, kwargs):
    if kwargs:
        url = reverse(name, kwargs=kwargs)
    else:
        url = reverse(name)
    match = resolve(url)
    assert match.func == view
