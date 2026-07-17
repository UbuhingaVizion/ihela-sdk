# Changelog

## [0.1.1] - Unreleased

### Fixed
- Fix `mypy` type-check errors: properly annotate `auth_token_object` as `dict | None` across all clients
- Remove dead `try/except ImportError` for `secrets` module (unreachable on Python 3.10+)
- Fix CI `pkg_meta` job: install `twine` before running check
- Fix CI `typecheck` job: add `[tool.mypy]` config with ignored missing stubs for `pydantic`, `httpx`, `django`, `allauth`

## [0.1.0] - 2026-07-17

### Added
- Initial release of `ihela-sdk` (migrated from `ihela-python-client`)
- New `BankingClient.request_token()` and `AgentClient.request_token()` for username/password token authentication
- New `BankingClient.transaction_fee()` endpoint for querying transaction fees
- `py.typed` marker for PEP 561 type-checking support
- Export `DepositPayload`, `WithdrawalPayload`, and `ValidateWithdrawalPayload` Pydantic models

### Changed
- **Breaking**: Module renamed from `ihela_client` to `ihela_sdk`
- **Breaking**: `MerchantClient.verify_bill()` signature changed to `(bill_code, merchant_reference, pin_code)` matching official API
- **Breaking**: `MerchantAuthorizationClient` constructor uses `prod=False` instead of `test=False`
- **Breaking**: `MerchantClient.verify_bill()`, `init_bill()`, and `cashin_client()` now send JSON (`Content-Type: application/json`) instead of form-encoded data
- **Breaking**: `bill_init()` sends official field names (`debit_account`, `debit_bank`, etc.)
- `BankingClient.deposit()` endpoint corrected to `make-deposit/` (was incorrectly using `agent-deposit/`)
- All `MerchantClient` HTTP calls now have `timeout=15.0` (were previously unbounded)
- Django views now use conditional `allauth` imports to avoid import errors for non-Django users
- Updated classifiers, keywords, project URLs, and metadata for PyPI

### Removed
- `MerchantClient.get_token_type()` unused `code` parameter removed

## Previous versions

For versions prior to 0.1.0, see [ihela-python-client changelog](https://pypi.org/project/ihela-python-client/).
