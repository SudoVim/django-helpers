from django.db import models
from django.urls import reverse


def get_admin_model_path(model: type[models.Model]) -> str:
    """
    Returns the admin path for the given *model*.
    """
    return f"{model._meta.app_label}/{model._meta.model_name}/"


def get_admin_page(
    model: type[models.Model], suffix: str, prefix: str = "admin:"
) -> str:
    """
    Returns the admin page name for the given *model* and *suffix*.
    """
    return f"{prefix}{model._meta.app_label}_{model._meta.model_name}_{suffix}"


def get_admin_change_url(obj: models.Model) -> str:
    """
    Returns the admin change URL for the given model instance.
    """
    return reverse(get_admin_page(obj.__class__, "change"), args=(obj.pk,))


def get_admin_list_url(model_type: type[models.Model]) -> str:
    """
    Get the admin list URL for the given model type.
    """
    return reverse(get_admin_page(model_type, "changelist"))


def get_admin_add_url(
    model_type: type[models.Model], query_params: dict[str, str] | None = None
) -> str:
    """
    Get the admin add URL for the given model type, optionally with query parameters.
    """
    url = reverse(get_admin_page(model_type, "add"))
    if query_params:
        from urllib.parse import urlencode

        url = f"{url}?{urlencode(query_params)}"

    return url
