import unittest

import os
from config_probe import probe, fake_probe
from hamcrest import is_, assert_that


class TestConfigProbe(unittest.TestCase):

    def test_single_file(self):
        config = probe(path=_dir("single-file"),
                       patterns=["stuff.yaml"])

        assert_that(config.key, is_("stuff-value"))

    def test_single_file_with_namespace(self):
        config = probe(path=_dir("single-file-with-namespace"),
                       patterns=["(*).json"])

        assert_that(config.stuff.key, is_("stuff-value"))

    def test_two_files_with_subdir_namespace(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["(*)/(*).yaml"])

        assert_that(config.ns1.stuff.key1, is_("stuff from ns1"))
        assert_that(config.ns2.stuff.key2, is_("stuff from ns2"))

    def test_only_starred_parts_are_namespaced(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["(*)/stuff.yaml"])

        assert_that(config.ns1.key1, is_("stuff from ns1"))
        assert_that(config.ns2.key2, is_("stuff from ns2"))

    def test_using_only_a_star_does_not_count_toward_namespacing(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["*/stuff.yaml"])

        assert_that(config.key1, is_("stuff from ns1"))
        assert_that(config.key2, is_("stuff from ns2"))

    def test_multiple_patterns(self):
        config = probe(path=_dir("two-files-with-subdir-namespace"),
                       patterns=["ns1/(*).yaml", "(*)/stuff.yaml"])

        assert_that(config.stuff.key1, is_("stuff from ns1"))
        assert_that(config.ns2.key2, is_("stuff from ns2"))

    def test_multiple_patterns_on_same_namespaces_should_merge_recursively(self):
        config = probe(path=_dir("multi-level-files"),
                       patterns=["(*)/(*).yaml", "(*)/subdir/(*).yaml"])

        assert_that(config.ns1.stuff.content1.key1, is_("value1"))
        assert_that(config.ns1.stuff.content2.key2, is_("value2"))

    def test_pattern_order_defines_which_files_have_the_authority(self):
        config = probe(path=_dir("key-override"),
                       patterns=["file1.yaml", "file2.yaml"])
        assert_that(config.key, is_("value2"))

        config = probe(path=_dir("key-override"),
                       patterns=["file2.yaml", "file1.yaml"])
        assert_that(config.key, is_("value1"))

    def test_support_for_empty_files(self):
        probe(path=_dir("empty-files"), patterns=["*.*"])

    def test_fake_probe(self):
        config = fake_probe({
            "key": "value",
            "key2": [
                {"hey": "ho"}
            ]
        })

        assert_that(config.key, is_("value"))
        assert_that(config.key2[0].hey, is_("ho"))


def _dir(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
