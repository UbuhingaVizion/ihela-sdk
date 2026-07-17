# Changelog

## [0.3.0] - 2026-07-17

### Added
- **Token injection**: All clients accept optional `token` parameter to skip
  authentication entirely. Pass `{"access_token": "...", "token_type": "Bearer"}`.
- **Deferred authentication**: `auto_auth=False` parameter defers authentication
  to the first API call — no HTTP call on `__init__`.
- **`clear_token()`**: Explicit token cleanup method on all clients.
- **Safe `__repr__`**: Client objects never expose credentials in string representations.
- **Framework-agnostic OAuth2 guide**: Documentation shows OAuth2 integration
  patterns for Django, Flask, and FastAPI without framework dependencies.

### Changed
- **Dropped `requests` dependency**: All synchronous clients now use `httpx.Client`.
  This removes ~5 transitive dependencies (`certifi`, `urllib3`, `charset-normalizer`,
  `idna`) and ensures sync/async clients share the same HTTP library, types, and
  error handling.
- Sync clients (`BankingClient`, `AgentClient`, `MerchantClient`,
  `MerchantAuthorizationClient`) now wrap HTTP calls in `with httpx.Client()`
  context managers instead of bare `requests.post/get` calls.
- `requests.RequestException` error handling replaced with `httpx.HTTPError`.

### Removed
- **Django views**: Removed `ihela_sdk.django` module. The SDK is now fully
  framework-agnostic. Use `MerchantAuthorizationClient` directly with any web
  framework (see Authentication guide).
- **Django extra**: `pip install ihela-sdk[django]` no longer exists.

### Security
- Removed unsafe `logger.debug(auth_data)` that logged credentials in plaintext.
- Extended `mask_sensitive_data()` to cover 10 sensitive key patterns (was 5).
- Credentials never appear in `__repr__`, logs, or error messages.

### Fixed
- Tox `d52`/`d60` environments: added `allowlist_externals = pytest` and
  explicit `pytest-cov` dependency.
- Publish workflow: tags are now verified to be on `master` before publishing.
- Docs theme updated to match iHelá branding (burgundy `#8A0625`).
- Docs deploy now only triggers on `master` push with doc changes.

## [0.1.1] - 2026-07-17

### Fixed
- Fix `mypy` type-check errors: properly annotate `auth_token_object` as
  `dict | None` across all clients.
- Remove dead `try/except ImportError` for `secrets` module (unreachable on
  Python 3.10+).
- Fix CI `pkg_meta` job: install `twine` before running check.
- Fix CI `typecheck` job: add `[tool.mypy]` config with ignored missing stubs
  for `pydantic`, `httpx`, `django`, `allauth`.

## [0.1.0] - 2026-07-17

### Added
- Initial release of `ihela-sdk` (migrated from `ihela-python-client`).
- New `BankingClient.request_token()` and `AgentClient.request_token()` for
  username/password token authentication.
- New `BankingClient.transaction_fee()` endpoint for querying transaction fees.
- `py.typed` marker for PEP 561 type-checking support.
- Export `DepositPayload`, `WithdrawalPayload`, and `ValidateWithdrawalPayload`
  Pydantic models.

### Changed
- **Breaking**: Module renamed from `ihela_client` to `ihela_sdk`.
- **Breaking**: `MerchantClient.verify_bill()` signature changed to
  `(bill_code, merchant_reference, pin_code)` matching official API.
- **Breaking**: `MerchantAuthorizationClient` constructor uses `prod=False`
  instead of `test=False`.
- **Breaking**: `MerchantClient.verify_bill()`, `init_bill()`, and
  `cashin_client()` now send JSON instead of form-encoded data.
- **Breaking**: `bill_init()` sends official field names (`debit_account`,
  `debit_bank`, etc.).
- `BankingClient.deposit()` endpoint corrected to `make-deposit/` (was incorrectly
  using `agent-deposit/`).
- All `MerchantClient` HTTP calls now have `timeout=15.0` (were previously unbounded).
- Django views now use conditional `allauth` imports to avoid import errors for
  non-Django users.
- Updated classifiers, keywords, project URLs, and metadata for PyPI.

### Removed
- `MerchantClient.get_token_type()` unused `code` parameter removed.

## Previous versions

For versions prior to 0.1.0, see
[ihela-python-client changelog](https://pypi.org/project/ihela-python-client/).
