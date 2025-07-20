# Toshy NixOS Flake Improvement Plan

## Overview

This document outlines a comprehensive plan for improving the Toshy NixOS flake implementation. The plan is divided into four phases, each addressing specific aspects of the codebase that need improvement.

## Background

Toshy is a Mac-style keybinding application for Linux that has been modernized from a complex Nix overlay to a clean, maintainable Nix flake. While the current implementation follows NixOS best practices, there are several areas that need improvement:

1. External applications should not be wrapped into the application
2. Test cases should test the frontend as well as the backend
3. toshy-tray and toshy-gui should be available from the CLI
4. Only toshy-tray should have a service, not toshy-gui
5. The requirements.txt should be accurate based on actual imports

## Improvement Phases

### [Phase 1: Dependency Analysis and Requirements Refinement](./PHASE1_DEPENDENCY_ANALYSIS.md)

**Objective:** Create an accurate requirements.txt by scanning all imports and remove external application wrapping.

**Key Tasks:**
- Scan all Python files for import statements
- Compare found dependencies with current requirements
- Identify and remove wrapped external applications
- Update flake.nix to directly call external applications
- Create an accurate requirements.txt

### [Phase 2: CLI Accessibility Improvement](./PHASE2_CLI_ACCESSIBILITY.md)

**Objective:** Ensure toshy-tray and toshy-gui are properly exposed as CLI commands.

**Key Tasks:**
- Verify entry points in pyproject.toml
- Ensure proper exposure in flake.nix
- Test direct CLI execution
- Add error handling and user feedback
- Update documentation

### [Phase 3: Service Configuration Optimization](./PHASE3_SERVICE_OPTIMIZATION.md)

**Objective:** Ensure only toshy-tray has a systemd service, not toshy-gui.

**Key Tasks:**
- Review current service configurations
- Modify the NixOS module
- Update the Home Manager module
- Ensure toshy-gui can be launched from tray
- Test service management

### [Phase 4: Frontend Testing Implementation](./PHASE4_FRONTEND_TESTING.md)

**Objective:** Develop comprehensive test cases for the frontend components.

**Key Tasks:**
- Set up frontend testing framework
- Create basic UI component tests
- Implement button click tests
- Test form input and validation
- Set up headless testing for CI/CD
- Integrate frontend tests with existing backend tests

## Implementation Strategy

Each phase will be implemented sequentially, with careful attention to maintaining backward compatibility and ensuring that the application continues to function correctly throughout the process. The implementation will follow these principles:

1. **Incremental Changes:** Make small, targeted changes that can be easily tested and verified
2. **Comprehensive Testing:** Test each change thoroughly to ensure it works as expected
3. **Documentation:** Update documentation to reflect the changes
4. **Backward Compatibility:** Ensure that existing users can continue to use the application

## Success Criteria

The improvement plan will be considered successful when:

1. External applications are no longer wrapped into the application
2. Test cases cover both frontend and backend functionality
3. toshy-tray and toshy-gui are available from the CLI
4. Only toshy-tray has a service, not toshy-gui
5. The requirements.txt accurately reflects the actual imports

## Timeline

Each phase is designed to be implemented independently, allowing for flexibility in the implementation timeline. However, the phases should be implemented in order, as later phases may depend on changes made in earlier phases.

## Conclusion

This improvement plan addresses the key issues identified in the current Toshy NixOS flake implementation. By following this plan, the codebase will become more maintainable, more user-friendly, and more robust.
