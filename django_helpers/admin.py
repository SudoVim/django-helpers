from collections.abc import Iterable
from typing import Any, TypeVar

from django.contrib import admin
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import URLPattern, path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.text import capfirst
from typing_extensions import override

from django_helpers.links import get_admin_add_url, get_admin_model_path, get_admin_page

M = TypeVar("M", bound=Model)


class DHModelAdmin(admin.ModelAdmin[M]):
    change_actions: tuple[str, ...] = tuple()

    @override
    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()
        custom_urls = [self.custom_route(a) for a in self.change_actions]
        return custom_urls + urls

    def custom_route(self, name: str) -> Any:
        """
        Generate a custom route.
        """
        return path(
            f"{get_admin_model_path(self.model)}<int:pk>/{name}/",
            self.admin_site.admin_view(getattr(self, name)),
            name=get_admin_page(self.model, name, prefix=""),
        )

    def action_buttons(self, obj: Model) -> str:
        if not obj.pk:
            return "-"
        html_buttons: list[str] = []
        for change_action in self.change_actions:
            url = reverse(
                get_admin_page(obj.__class__, change_action),
                args=[obj.pk],
            )
            html_buttons.append(
                format_html(
                    '<a class="button" href="{}">{}</a>',
                    url,
                    capfirst(change_action.replace("_", " ")),
                ),
            )

        return format_html_join(
            " | ",
            "{}",
            [[b] for b in html_buttons],
        )

    def action_button(self, obj: Model, change_action: str):
        """
        Generate an action button HTML with the given *url* and
        *change_action*.
        """
        url = reverse(
            get_admin_page(obj.__class__, change_action),
            args=[obj.pk],
        )
        return format_html(
            '<a class="button" href="{}">{}</a>',
            url,
            capfirst(change_action.replace("_", " ")),
        )

    def confirm_action_button(
        self, obj: Model, change_action: str, confirm_message: str
    ):
        """
        Generate an action button HTML with the given *url* and *change_action*
        behind an alert prompt.
        """
        url = reverse(
            get_admin_page(obj.__class__, change_action),
            args=[obj.pk],
        )
        return format_html(
            """\
<a class="confirm-and-then-do button" href="#" data-confirm-message="{}" data-target-url="{}">
{}
</a>
""",
            confirm_message,
            url,
            capfirst(change_action.replace("_", " ")),
        )

    def redirect(self, link: str) -> HttpResponse:
        """
        Send the user to the given *link*
        """
        return redirect(link)

    def redirect_referrer(self, request: HttpRequest) -> HttpResponse:
        """
        Send the user back to the referrer
        """
        return redirect(request.META.get("HTTP_REFERER", "admin:index"))

    def redirect_add_model(
        self, model_type: type[Model], query_params: dict[str, str] | None = None
    ) -> HttpResponse:
        """
        Return a response that redirects a user to the "add" page for the given
        *model_type* and *query_params*.
        """
        return self.redirect(get_admin_add_url(model_type, query_params=query_params))

    def generate_table(
        self, headers: Iterable[str], data: Iterable[Iterable[Any]]
    ) -> str:
        """
        Generate a HTML table from the given *headers* and *data*.
        """
        return format_html(
            "<table><thead><tr>{}</tr></thead><tbody>{}</tbody></table>",
            format_html_join("", "<th>{}</th>", [[h] for h in headers]),
            format_html_join(
                "",
                "<tr>{}</tr>",
                [
                    [
                        format_html_join(
                            "",
                            "<td>{}</td>",
                            [[str(v)] for v in r],
                        )
                    ]
                    for r in data
                ],
            ),
        )
