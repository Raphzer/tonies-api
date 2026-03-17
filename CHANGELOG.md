# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-02-01

### Added
- Initial release of `tonies-api`.
- Asynchronous client (`TonieAPIClient`) for Tonies REST and GraphQL APIs.
- WebSocket client (`TonieWebSocket`) for real-time events.
- OAuth2 authentication flow with Keycloak support.
- Pydantic models for data validation.

## [0.1.2] - 2026-02-01

### Added
- `is_tng` property to `Toniebox` model for easy identification of Toniebox Go.
- `bedtime_schedules` property to `Toniebox` model for easy access to bedtime schedules.

### Changed
- Refactored `TonieResources` to use `is_tng` property instead of checking `features` dictionary.
- Added caching for `_get_toniebox` method to reduce API calls.

### Fixed
- Fixed `set_max_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_max_headphone_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_light_brightness` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_bedtime_max_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_bedtime_max_headphone_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_bedtime_light_brightness` method to use `is_tng` property instead of checking `features` dictionary.

## [0.1.3] - 2026-03-18

### Added
- `is_tng` property to `Toniebox` model for easy identification of Toniebox Go.
- `bedtime_schedules` property to `Toniebox` model for easy access to bedtime schedules.

### Changed
- Refactored `TonieResources` to use `is_tng` property instead of checking `features` dictionary.
- Added caching for `_get_toniebox` method to reduce API calls.

### Fixed
- Fixed `set_max_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_max_headphone_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_light_brightness` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_bedtime_max_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_bedtime_max_headphone_volume` method to use `is_tng` property instead of checking `features` dictionary.
- Fixed `set_bedtime_light_brightness` method to use `is_tng` property instead of checking `features` dictionary.
