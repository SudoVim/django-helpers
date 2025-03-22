import pprint
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

from django.test import TestCase as DjangoTestCase
from typing_extensions import override


class MockTestCase(TestCase):
    module: str | None = None
    maxDiff: Any = None

    @override
    def setUp(self) -> None:
        super().setUp()

        self.module = None
        self.maxDiff = None

    def set_module(self, module: str) -> None:
        """
        Set the module to be used with :meth:`patch_module`.
        """
        self.module = module

    def patch_module(self, suffix: str, *args: Any, **kwargs: Any) -> MagicMock:
        """
        Patch object denoted by the given *suffix* on the configured module.
        """
        assert self.module is not None

        return self.patch(".".join([self.module, suffix]), *args, **kwargs)

    def patch(
        self,
        module_path: str,
        *args: Any,
        **kwargs: Any,
    ) -> MagicMock:
        """
        Patch the given module path for the life of this test and return it.
        """
        p = patch(module_path, *args, **kwargs)
        mock = p.start()
        self.addCleanup(p.stop)

        return mock

    def assertCalls(
        self,
        cmp_calls: list[Any],
        mock_calls: list[Any] | Any,
    ):
        """
        Assert that the given *cmp_calls* match the given *mock_calls*. If the
        assertion fails, print the two call lists for debug.
        """
        if not isinstance(mock_calls, list):
            mock_calls = mock_calls.mock_calls

        try:
            self.assertEqual(cmp_calls, mock_calls)

        except AssertionError:
            raise AssertionError(
                f"{pprint.pformat(cmp_calls)} != {pprint.pformat(mock_calls)}",  # pyright: ignore[reportUnknownArgumentType]
            )

    def assertAttrs(self, cmp_attrs: tuple[Any, ...], obj: Any, *attrs: str) -> None:
        """
        Assert that the given *attrs* of *obj* match the given *cmp_attrs*.
        """
        is_attrs = self.getattrs(obj, *attrs)
        try:
            self.assertEqual(cmp_attrs, is_attrs)

        except AssertionError:
            raise AssertionError(
                f"{pprint.pformat(cmp_attrs)} != {pprint.pformat(is_attrs)}",
            )

    def getattrs(self, obj: Any, *attrs: str) -> tuple[Any]:
        """
        Get and return a ``tuple`` of attrs from the given *obj* corresponding
        to the given *attrs* strings.
        """
        return tuple(getattr(obj, a) for a in attrs)


class DHTestCase(DjangoTestCase, MockTestCase):
    _base_set_up: bool = False

    @override
    def setUp(self):
        super().setUp()

        self._base_set_up = True

    @override
    def tearDown(self):
        super().tearDown()

        if not hasattr(self, "_base_set_up"):
            raise RuntimeError("setUp of DHTestCase was not called")
