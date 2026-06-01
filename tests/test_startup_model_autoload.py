from faster_whisper_GUI.mainWindows import should_auto_load_model
from faster_whisper_GUI.mainWindows import MainWindows


class FakeSwitch:
    def __init__(self, checked):
        self.checked = checked

    def isChecked(self):
        return self.checked


class FakeSettingsPage:
    def __init__(self, auto_load_enabled):
        self.switchButton_autoLoadModel = FakeSwitch(auto_load_enabled)


def test_startup_model_autoload_skips_when_switch_is_off():
    assert not should_auto_load_model(False, {"model_size_or_path": "large-v3"})


def test_startup_model_autoload_skips_empty_local_model_path():
    assert not should_auto_load_model(True, {"model_size_or_path": ""})


def test_startup_model_autoload_skips_whitespace_model_target():
    assert not should_auto_load_model(True, {"model_size_or_path": "   "})


def test_startup_model_autoload_runs_when_model_target_exists():
    assert should_auto_load_model(True, {"model_size_or_path": "large-v3"})


def test_startup_model_autoload_calls_model_loader_when_ready():
    calls = []
    window = type(
        "FakeWindow",
        (),
        {
            "page_setting": FakeSettingsPage(True),
            "getParam_model": lambda self: {"model_size_or_path": "large-v3"},
            "onModelLoadClicked": lambda self: calls.append("loaded"),
        },
    )()

    MainWindows.autoLoadModelOnStartup(window)

    assert calls == ["loaded"]


def test_startup_model_autoload_does_not_call_model_loader_without_target():
    calls = []
    window = type(
        "FakeWindow",
        (),
        {
            "page_setting": FakeSettingsPage(True),
            "getParam_model": lambda self: {"model_size_or_path": ""},
            "onModelLoadClicked": lambda self: calls.append("loaded"),
        },
    )()

    MainWindows.autoLoadModelOnStartup(window)

    assert calls == []
