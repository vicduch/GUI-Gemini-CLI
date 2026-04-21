import os
import json
import pytest
from core.config_manager import ConfigManager

def test_config_manager_load_save(tmp_path):
    config_file = tmp_path / "config.json"
    manager = ConfigManager(str(config_file))
    
    # Test default values
    assert manager.get("theme", "system") == "system"
    
    # Test save
    manager.set("theme", "dark")
    manager.save()
    
    # Verify file content
    with open(config_file, "r") as f:
        data = json.load(f)
        assert data["theme"] == "dark"
    
    # Test load in new manager
    new_manager = ConfigManager(str(config_file))
    assert new_manager.get("theme") == "dark"

def test_config_manager_nested_get(tmp_path):
    config_file = tmp_path / "config.json"
    manager = ConfigManager(str(config_file))
    
    manager.set("ui", {"sidebar": {"width": 250}})
    assert manager.get("ui")["sidebar"]["width"] == 250

def test_config_manager_save_no_parent(tmp_path):
    # Test saving a config file in a directory that is the current working directory
    # (i.e., os.path.dirname is empty)
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config_file = "local_config.json"
        manager = ConfigManager(config_file)
        manager.set("key", "value")
        # This should not raise FileNotFoundError: [Errno 2] No such file or directory: ''
        manager.save()
        assert os.path.exists(config_file)
    finally:
        os.chdir(original_cwd)
