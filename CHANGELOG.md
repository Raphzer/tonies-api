# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-02-01

### Added
- Initial release of `tonies-api`.
- Asynchronous client (`TonieAPIClient`) for Tonies REST and GraphQL APIs.
- WebSocket client (`TonieWebSocket`) for real-time events.
- OAuth2 authentication flow with Keycloak support.
- Pydantic models for data validation.

## [0.1.4] - 2026-03-18

### Fixed
- Fixed `Toniebox` Pydantic v2 model: `Optional` fields (`lightring_brightness`, `bedtime_lightring_brightness`, `bedtime_lightring_color`, `bedtime_max_volume`, `bedtime_max_headphone_volume`) were missing `default=None`, making them implicitly required and causing `ValidationError` when parsing partial responses from PATCH endpoints (e.g. `set_max_volume`, `set_max_headphone_volume`).
- Fixed `bedtime_schedules` field missing `default_factory=list`, causing the same `ValidationError` on Classic boxes that don't return bedtime data.

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
