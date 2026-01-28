import pytest
from django.urls import reverse

NO_PK = [
    ("resources", None),
    ("add_resource", None),
]

WITH_PK = [
    ("resource_detail", {"pk": 1}),
    ("edit_resource", {"pk": 1}),
    ("delete_resource", {"pk": 1}),
    ("download_resource", {"pk": 1}),
]

@pytest.mark.django_db
@pytest.mark.parametrize("name,kwargs", NO_PK + WITH_PK)
def test_get_endpoints_do_not_500_as_anonymous(client, name, kwargs):
    url = reverse(name, kwargs=kwargs) if kwargs else reverse(name)
    resp = client.get(url)
    # We don’t care if it redirects or 404s right now, only that it doesn’t 500
    assert resp.status_code < 500
