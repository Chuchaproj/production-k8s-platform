# Local image security report

Scan date: 2026-10-03. Tool: Trivy 0.75.0. Image scan executed locally; this is not a clean-security certificate.

The patched Debian 13 base still reports 44 HIGH, 60 MEDIUM, 60 LOW and 2 UNKNOWN findings. No CRITICAL finding was reported. None of the HIGH findings has a fixed Debian package version in the scan result. Runtime Python dependencies were checked separately where applicable; build tools pip/setuptools/wheel were removed from the image. Reachability/exploitability of the remaining OS findings was not audited.

These findings are disclosed, not hidden by an ignore file. The CI Trivy step is a reporting step with exit-code 0; it is not a blocking vulnerability gate. This trusted localhost lab must not be treated as internet-ready production. The scan covers the custom backend image, not every third-party stack image. Refresh the scan before publication and before any wider deployment.

| Advisory | Package | Installed version |
|---|---|---|
| CVE-2026-76642 | bsdutils | 1:2.41.5-0+deb13u1 |
| CVE-2026-78408 | bsdutils | 1:2.41.5-0+deb13u1 |
| CVE-2026-78409 | bsdutils | 1:2.41.5-0+deb13u1 |
| CVE-2026-78410 | bsdutils | 1:2.41.5-0+deb13u1 |
| CVE-2026-54369 | libacl1 | 2.3.2-2+b1 |
| CVE-2026-76642 | libblkid1 | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | libblkid1 | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | libblkid1 | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | libblkid1 | 2.41.5-0+deb13u1 |
| CVE-2026-76642 | liblastlog2-2 | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | liblastlog2-2 | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | liblastlog2-2 | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | liblastlog2-2 | 2.41.5-0+deb13u1 |
| CVE-2026-76642 | libmount1 | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | libmount1 | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | libmount1 | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | libmount1 | 2.41.5-0+deb13u1 |
| CVE-2025-69720 | libncursesw6 | 6.5+20250216-2 |
| CVE-2026-76642 | libsmartcols1 | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | libsmartcols1 | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | libsmartcols1 | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | libsmartcols1 | 2.41.5-0+deb13u1 |
| CVE-2026-16742 | libsystemd0 | 257.13-1~deb13u1 |
| CVE-2025-69720 | libtinfo6 | 6.5+20250216-2 |
| CVE-2026-16742 | libudev1 | 257.13-1~deb13u1 |
| CVE-2026-76642 | libuuid1 | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | libuuid1 | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | libuuid1 | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | libuuid1 | 2.41.5-0+deb13u1 |
| CVE-2026-76642 | login | 1:4.16.0-2+really2.41.5-0+deb13u1 |
| CVE-2026-78408 | login | 1:4.16.0-2+really2.41.5-0+deb13u1 |
| CVE-2026-78409 | login | 1:4.16.0-2+really2.41.5-0+deb13u1 |
| CVE-2026-78410 | login | 1:4.16.0-2+really2.41.5-0+deb13u1 |
| CVE-2026-76642 | mount | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | mount | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | mount | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | mount | 2.41.5-0+deb13u1 |
| CVE-2025-69720 | ncurses-base | 6.5+20250216-2 |
| CVE-2025-69720 | ncurses-bin | 6.5+20250216-2 |
| CVE-2026-9538 | perl-base | 5.40.1-6+deb13u1 |
| CVE-2026-76642 | util-linux | 2.41.5-0+deb13u1 |
| CVE-2026-78408 | util-linux | 2.41.5-0+deb13u1 |
| CVE-2026-78409 | util-linux | 2.41.5-0+deb13u1 |
| CVE-2026-78410 | util-linux | 2.41.5-0+deb13u1 |
