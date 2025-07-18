#!/usr/bin/env python3
"""
Tests for the NixOS module integration
"""

import pytest
import tempfile
import os
from pathlib import Path

def test_nixos_module_structure():
    """Test that the NixOS module has the expected structure"""
    module_path = Path(__file__).parent.parent / "modules" / "toshy.nix"
    assert module_path.exists(), "NixOS module file should exist"
    
    # Read the module content
    content = module_path.read_text()
    
    # Check for key components
    assert "services.toshy" in content, "Module should define services.toshy options"
    assert "systemd.user.services.toshy" in content, "Module should define systemd user service"
    assert "enable = mkEnableOption" in content, "Module should have enable option"
    assert "package = mkPackageOption" in content, "Module should have package option"

def test_flake_structure():
    """Test that the flake has the expected outputs"""
    flake_path = Path(__file__).parent.parent / "flake.nix"
    assert flake_path.exists(), "Flake file should exist"
    
    content = flake_path.read_text()
    
    # Check for key outputs
    assert "packages" in content, "Flake should define packages"
    assert "devShells" in content, "Flake should define devShells"
    assert "nixosModules" in content, "Flake should define nixosModules"
    assert "overlays" in content, "Flake should define overlays"

def test_pyproject_structure():
    """Test that pyproject.toml has the expected structure"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml should exist"
    
    content = pyproject_path.read_text()
    
    # Check for key sections
    assert "[project.scripts]" in content, "Should define entry point scripts"
    assert "toshy-tray" in content, "Should define toshy-tray entry point"
    assert "toshy-daemon" in content, "Should define toshy-daemon entry point"
    assert "[tool.pytest.ini_options]" in content, "Should have pytest configuration"

if __name__ == "__main__":
    pytest.main([__file__])
