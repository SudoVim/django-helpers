from unittest import TestCase

from django_helpers.prefetch import prefetch


class PrefetchTests(TestCase):
    def test_only_strings(self) -> None:
        self.assertEqual({"a__b__c"}, prefetch("a", "b", "c"))

    def test_strings_to_list(self) -> None:
        self.assertEqual(
            {
                "a__b__c",
                "a__b__d",
                "a__b__e",
            },
            prefetch("a", "b", ["c", "d", "e"]),
        )

    def test_none_prefix(self) -> None:
        self.assertEqual(
            {
                "calculation__months",
                "calculation__costs__months",
            },
            prefetch(
                None,
                [
                    "calculation__months",
                    "calculation__costs__months",
                ],
            ),
        )
