# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0-beta] - 2025-01-15

### Added
- Intelligence Information Report (IIR) system for operations
- Direct messaging system with inbox UI
- Message router to prevent socket race conditions
- DTG (Date-Time Group) format for military-style timestamps
- Database connection pooling
- Rate limiting for messages and file uploads
- File upload validation (size, MIME type)
- Environment variable support for encryption secrets
- Comprehensive test suite for Sudoku components

### Changed
- Simplified IIR display to 3/4 box format for better readability
- Improved authentication with token-based system
- Enhanced security with input validation
- Reorganized project structure (docs/ and assets/ directories)
- Updated default server address to localhost (127.0.0.1)

### Security
- Removed hardcoded passwords and sensitive data from repository
- Moved encryption secrets to environment variables
- Added SQL injection protection via parameterized queries
- Implemented file upload sanitization
- Added session token management

### Fixed
- Socket race condition in message handling
- IIR border wrapping and display issues
- Color bleed in formatted text displays
- Windows socket compatibility issues
- Thread safety in GUI operations

## [0.1.0] - 2024-10-20

### Added
- Initial Sudoku game with CLI and GUI interfaces
- Puzzle generator with multiple difficulty levels
- Backtracking solver algorithm
- Chat system with operations/wiki features
- Tailscale network integration
- Server GUI with real-time logging
- Anonymous chat mode

---

## Planned for v1.0.0

### To Add
- Comprehensive chat system tests
- Installation script
- Configuration wizard
- More robust error handling
- Enhanced documentation

### To Improve
- Password strength requirements for chat registration
- TLS/SSL option alongside Tailscale
- Database initialization automation
- Setup and deployment guides
