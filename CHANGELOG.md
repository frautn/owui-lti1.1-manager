# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added
- Direct non-Moodle password login screen at `/login/`.
- List of Questions.
- Edit/Remove questions.


<!-- ### ⚠️ Admin & LTI Integration Action Required -->
<!-- - **Moodle Admins:** Re-synchronize LTI 1.3 keys. A new claim `https://purl.imsglobal.org/spec/lti/claim/custom` was added to consumer configurations. -->
<!-- - Environment variable `LTI_CONSUMERS` schema has updated to JSON dictionary format. -->

<!-- ### Added -->
<!-- - Account linking workflow for users logging in via both LTI and standard forms. -->

<!-- ### Changed -->
<!-- - Refactored `AUTHENTICATION_BACKENDS` pipeline to evaluate `LTI13AuthBackend` prior to standard Django `ModelBackend`. -->

<!-- ### Fixed -->
<!-- - Fixed `SameSite=None` cookie drop on Safari when loaded inside Moodle `<iframe>`. -->
<!-- - Resolved user email collisions during LTI auto-provisioning. -->

<!-- ### Security -->
<!-- - Fixed unauthenticated access risk on public media uploads (`CVE-YYYY-XXXX`). -->


## [0.1.0] - 2026-08-04

It's a simple hompage that shows the information sent by Moodle.

### Added
- Initial LTI 1.1 launch provider support.
- Auto signin.
- Homepage with info sent by Moodle.

---

<!-- [Unreleased]: https://github.com/your-org/your-app/compare/v1.2.0...HEAD -->
<!-- [1.2.0]: https://github.com/your-org/your-app/compare/v1.1.0...v1.2.0 -->
[0.1.0]: https://github.com/frautn/owui-lti1.1-manager/releases/tag/v0.1.0