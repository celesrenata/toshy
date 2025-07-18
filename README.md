# Toshy Nix Flake Modernization Project

This directory contains context files and planning documents for modernizing the Toshy application packaging from a complex Nix overlay to a clean, maintainable Nix flake following modern Nix practices.

## Project Overview

Toshy is a Mac-style keybinding application for Linux that currently uses an outdated and problematic Nix overlay for packaging. This project aims to completely restructure the packaging approach using modern Nix flakes and best practices.

## Context Files

### Analysis Documents
- **[MODERNIZATION_CONTEXT.md](./MODERNIZATION_CONTEXT.md)** - Overview of current problems and modernization goals
- **[DEPENDENCY_ANALYSIS.md](./DEPENDENCY_ANALYSIS.md)** - Detailed analysis of dependencies and recommendations
- **[PACKAGING_ISSUES.md](./PACKAGING_ISSUES.md)** - Critical issues in current implementation and solutions

### Design Documents
- **[FLAKE_ARCHITECTURE.md](./FLAKE_ARCHITECTURE.md)** - Proposed flake structure and design principles
- **[NIXOS_MODULE_DESIGN.md](./NIXOS_MODULE_DESIGN.md)** - NixOS module design and configuration options

### Implementation Guides
- **[DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)** - Phased development plan with timeline
- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Guide for migrating from overlay to flake

## Key Problems Identified

1. **Duplicate Package Definitions**: Multiple unnecessary `-init` variants
2. **Incorrect Nix Syntax**: Case sensitivity issues (`BuildInputs` vs `buildInputs`)
3. **Poor Dependency Management**: Improper use of build/runtime dependencies
4. **Manual Installation**: Shell scripts instead of proper Python packaging
5. **Complex Overlay Structure**: Overly complicated when simpler approaches exist
6. **Missing Modern Features**: No flake structure, development environment, or proper testing

## Modernization Goals

1. **Convert to Nix Flake**: Modern flake.nix with proper structure
2. **Proper Python Packaging**: Use buildPythonApplication correctly
3. **Clean Dependencies**: Use nixpkgs packages where available
4. **NixOS Integration**: Full NixOS module with service management
5. **Development Experience**: Comprehensive development environment
6. **Documentation**: Clear usage and development documentation

## Next Steps

1. **Review Context Files**: Read through all analysis and design documents
2. **Set Up Development Environment**: Create initial flake structure
3. **Begin Phase 1**: Implement basic flake and package cleanup
4. **Follow Development Plan**: Execute the 10-week phased approach

## Benefits of Modernization

- **Simplified Management**: No complex overlay maintenance
- **Better Integration**: Proper NixOS service integration
- **Easier Updates**: Flake-based version management
- **Improved Development**: Comprehensive development environment
- **Better Testing**: Integrated test infrastructure
- **Clear Documentation**: Usage and development guides

## Timeline

The project is planned as a 10-week effort divided into 5 phases:
1. **Foundation** (2 weeks): Basic flake structure and dependency cleanup
2. **Core Package** (2 weeks): Main application packaging
3. **NixOS Integration** (2 weeks): System integration and services
4. **Advanced Features** (2 weeks): Multi-platform and Home Manager support
5. **Documentation & Polish** (2 weeks): Final documentation and quality assurance

## Getting Started

To begin implementation:

1. Read through the context files to understand the current state and goals
2. Review the proposed architecture in `FLAKE_ARCHITECTURE.md`
3. Follow the development plan in `DEVELOPMENT_PLAN.md`
4. Use the migration guide when ready to transition users

This modernization will transform Toshy from a problematic overlay into a well-structured, maintainable Nix flake that follows current best practices and provides an excellent user experience.
