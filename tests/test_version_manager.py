import pytest

# Testing library and framework: pytest (functional style with parametrize and exception assertions)

# We attempt flexible imports to accommodate various project layouts.
try:
    # Typical package import (adjust if project has a specific root package)
    from src.version_manager import VersionManager  # type: ignore
except ImportError:
    try:
        # Alternative common layout: package module path
        from version_manager import VersionManager  # type: ignore
    except ImportError:
        # Fallback: relative path within a package structure; update as needed
        from ..src.version_manager import VersionManager  # type: ignore

# Import exceptions with similar flexibility
try:
    from src.exceptions import NoLiveVersionError, MultipleLiveVersionsError, VersionNotFoundError  # type: ignore
except ImportError:
    try:
        from exceptions import NoLiveVersionError, MultipleLiveVersionsError, VersionNotFoundError  # type: ignore
    except ImportError:
        from ..src.exceptions import NoLiveVersionError, MultipleLiveVersionsError, VersionNotFoundError  # type: ignore

def make_versions(**overrides):
    """
    Helper to build a minimal valid versions mapping with an overridable base.
    Structure mirrors what VersionManager expects in snippets.
    """
    base = {
        "v1": {
            "is_live": False,
            "provider": "openai",
            "config": {"model": "gpt-4o", "system_instruction": "You are helpful."},
            "tools_config": {},
            "description": "First version"
        },
        "v2": {
            "is_live": True,
            "provider": "openai",
            "config": {"model": "gpt-4o", "system_instruction": "Be concise."},
            "tools_config": {"web": {"enabled": True}},
            "description": "Live version"
        }
    }
    base.update(overrides)
    return base


class TestFindLiveVersion:
    def test_returns_live_version_key_when_single_live_present(self):
        vm = VersionManager()
        versions = make_versions()
        assert vm.find_live_version(versions, prompt_name="demo") == "v2"

    def test_raises_no_live_version_error_when_none_live(self):
        vm = VersionManager()
        versions = make_versions(v2={**make_versions()["v2"], "is_live": False})
        with pytest.raises(NoLiveVersionError) as exc:
            vm.find_live_version(versions, prompt_name="demo")
        msg = str(exc.value)
        # Should mention prompt name and available versions
        assert "demo" in msg
        assert "v1" in msg and "v2" in msg

    def test_raises_multiple_live_versions_error(self):
        vm = VersionManager()
        versions = make_versions(v1={**make_versions()["v1"], "is_live": True})
        with pytest.raises(MultipleLiveVersionsError) as exc:
            vm.find_live_version(versions, prompt_name="demo")
        # Should list live versions
        assert "v1" in str(exc.value) and "v2" in str(exc.value)

    @pytest.mark.parametrize(
        "flag", [True, 1, "yes"]  # truthy variants to ensure boolean evaluation via get("is_live", False)
    )
    def test_truthy_is_live_values_are_respected(self, flag):
        vm = VersionManager()
        versions = make_versions()
        versions["v2"]["is_live"] = flag
        assert vm.find_live_version(versions, prompt_name="demo") == "v2"


class TestGetVersionData:
    def test_returns_specific_version_when_present(self):
        vm = VersionManager()
        versions = make_versions()
        data = vm.get_version_data(versions, version="v1", prompt_name="demo")
        assert data["config"]["model"] == "gpt-4o"
        assert data["is_live"] is False

    def test_raises_version_not_found_error_for_missing_specific_version(self):
        vm = VersionManager()
        versions = make_versions()
        with pytest.raises(VersionNotFoundError) as exc:
            vm.get_version_data(versions, version="v9", prompt_name="demo")
        msg = str(exc.value)
        assert "v9" in msg and "demo" in msg
        # Available versions should be referenced
        assert "v1" in msg and "v2" in msg

    def test_returns_live_version_data_when_version_is_none(self):
        vm = VersionManager()
        versions = make_versions()
        data = vm.get_version_data(versions, version=None, prompt_name="demo")
        assert data["description"] == "Live version"

    def test_propagates_no_live_version_error_when_none_live(self):
        vm = VersionManager()
        versions = make_versions(v2={**make_versions()["v2"], "is_live": False})
        with pytest.raises(NoLiveVersionError):
            vm.get_version_data(versions, version=None, prompt_name="demo")

    def test_propagates_multiple_live_versions_error(self):
        vm = VersionManager()
        versions = make_versions(v1={**make_versions()["v1"], "is_live": True})
        with pytest.raises(MultipleLiveVersionsError):
            vm.get_version_data(versions, version=None, prompt_name="demo")


class TestGetSystemInstruction:
    def test_returns_system_instruction_when_present(self):
        vm = VersionManager()
        versions = make_versions()
        v2 = versions["v2"]
        assert vm.get_system_instruction(v2, prompt_name="demo") == "Be concise."

    @pytest.mark.parametrize(
        "bad_version_data",
        [
            {},  # no config at all
            {"config": {}},  # config exists but no system_instruction
            {"config": {"system_instruction": ""}},  # empty string should be considered missing
        ],
    )
    def test_raises_value_error_when_missing_system_instruction(self, bad_version_data):
        vm = VersionManager()
        with pytest.raises(ValueError) as exc:
            vm.get_system_instruction(bad_version_data, prompt_name="demo")
        assert "config.system_instruction" in str(exc.value)


class TestListVersions:
    def test_lists_all_versions_with_expected_shape_and_defaults(self):
        vm = VersionManager()
        versions = make_versions()
        # Add a version with minimal fields to check defaults
        versions["v3"] = {"config": {}, "description": "No model", "tools_config": {}}
        lst = vm.list_versions(versions)

        # Convert to dict keyed by version for easier assertions
        by_key = {item["version"]: item for item in lst}
        assert set(by_key.keys()) >= {"v1", "v2", "v3"}

        assert by_key["v1"]["is_live"] is False
        assert by_key["v1"]["provider"] == "openai"
        assert by_key["v1"]["model"] == "gpt-4o"
        assert by_key["v1"]["has_tools"] is False

        assert by_key["v2"]["is_live"] is True
        assert by_key["v2"]["has_tools"] is True
        assert by_key["v2"]["description"] == "Live version"

        # Defaults for missing values
        assert by_key["v3"]["provider"] == "unknown"
        assert by_key["v3"]["model"] == "unknown"
        assert by_key["v3"]["has_tools"] is False
        assert by_key["v3"]["description"] == "No model"

    def test_handling_empty_versions_map_returns_empty_list(self):
        vm = VersionManager()
        assert vm.list_versions({}) == []


class TestValidateVersionData:
    def test_valid_data_returns_true(self):
        vm = VersionManager()
        versions = make_versions()
        assert vm.validate_version_data(versions["v2"], prompt_name="demo", version="v2") is True

    @pytest.mark.parametrize(
        "mutator,expected_fragment",
        [
            (lambda d: d.pop("config", None), "Configuration section is missing"),
            (lambda d: d.setdefault("config", {}).pop("system_instruction", None), "System instruction is missing"),
            (lambda d: d.setdefault("config", {}).pop("model", None), "Model is missing"),
        ],
    )
    def test_missing_required_fields_raise_value_error_with_clear_message(self, mutator, expected_fragment):
        vm = VersionManager()
        data = make_versions()["v2"]
        # Deep-copy-ish manual clone to avoid mutating shared structure
        data = {
            "is_live": data.get("is_live"),
            "provider": data.get("provider"),
            "config": {**data.get("config", {})},
            "tools_config": {**data.get("tools_config", {})},
            "description": data.get("description", ""),
        }
        mutator(data)
        with pytest.raises(ValueError) as exc:
            vm.validate_version_data(data, prompt_name="demo", version="v2")
        msg = str(exc.value)
        assert "Invalid version data for 'demo' version 'v2'" in msg
        assert expected_fragment in msg


class TestPrivateGetNestedField:
    @pytest.mark.parametrize(
        "data,field,expected",
        [
            ({"a": {"b": {"c": 3}}}, "a.b.c", 3),
            ({"a": {"b": {"c": None}}}, "a.b.c", None),
            ({"a": {"b": 5}}, "a.b.c", None),
            ({}, "a", None),
            ({"config": {"model": "m"}}, "config.model", "m"),
        ],
    )
    def test_get_nested_field_various_paths(self, data, field, expected):
        vm = VersionManager()
        assert vm._get_nested_field(data, field) == expected

    def test_get_nested_field_non_dict_breaks_path_and_returns_none(self):
        vm = VersionManager()
        data = {"a": 1}
        assert vm._get_nested_field(data, "a.b") is None


def test_logger_injection_is_stored_but_not_required():
    dummy_logger = object()
    vm = VersionManager(logger=dummy_logger)
    # Access the name-mangled/private field to assert storage without relying on logger behavior
    assert getattr(vm, "_logger", None) is dummy_logger