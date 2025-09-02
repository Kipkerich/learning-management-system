import pytest
from django.urls import reverse, resolve
from resources import views

@pytest.mark.parametrize(
    "name,view,kwargs",
    [
        ("resources", views.resources_view, None),
        ("add_resource", views.add_resource, None),
        ("resource_detail", views.resource_detail, {"pk": 1}),
        ("edit_resource", views.edit_resource, {"pk": 1}),
        ("delete_resource", views.delete_resource, {"pk": 1}),
        ("download_resource", views.download_resource, {"pk": 1}),
    ],
)
def test_urls_resolve_to_correct_views(name, view, kwargs):
    if kwargs:
        url = reverse(name, kwargs=kwargs)
    else:
        url = reverse(name)
    match = resolve(url)
    assert match.func == view
