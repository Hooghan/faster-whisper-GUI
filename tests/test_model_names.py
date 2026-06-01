from faster_whisper.utils import available_models

from faster_whisper_GUI.config import Model_names


def test_gui_model_names_include_supported_non_alias_faster_whisper_121_short_names():
    installed_models = set(available_models())

    assert "distil-large-v3.5" in installed_models
    assert "distil-large-v3.5" in Model_names


def test_gui_model_names_omit_aliases_that_duplicate_explicit_model_names():
    assert "large" not in Model_names
    assert "turbo" not in Model_names


def test_existing_large_v3_turbo_index_is_preserved_for_saved_configs():
    assert Model_names[11] == "large-v3-turbo"


def test_model_name_list_keeps_original_model_indices_before_new_entries():
    assert Model_names[:12] == [
        "tiny",
        "tiny.en",
        "base",
        "base.en",
        "small",
        "small.en",
        "medium",
        "medium.en",
        "large-v1",
        "large-v2",
        "large-v3",
        "large-v3-turbo",
    ]


def test_distil_large_v35_is_listed_before_distil_large_v3():
    assert Model_names.index("distil-large-v3.5") < Model_names.index("distil-large-v3")


def test_model_name_list_keeps_distil_family_after_new_v35_entry():
    assert Model_names[12:] == [
        "distil-large-v3.5",
        "distil-large-v3",
        "distil-large-v2",
        "distil-medium.en",
        "distil-small.en",
    ]
