import pytest

from traceleak.openssl_derived_metadata_profile_demo_chain import (
    build_openssl_derived_metadata_profile_demo_chain,
)
from traceleak.openssl_derived_metadata_profile_report import (
    OpenSSLDerivedMetadataProfileReportError,
    render_openssl_derived_metadata_profile_report,
    validate_openssl_derived_metadata_profile_report,
    write_openssl_derived_metadata_profile_report,
)


def test_profile_report_renders_required_sections() -> None:
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]

    markdown = render_openssl_derived_metadata_profile_report(summary)

    assert "# OpenSSL-Derived Metadata Profile Report" in markdown
    assert "## Safety boundary" in markdown
    assert "## Baseline metrics" in markdown
    assert "## NN metrics" in markdown
    assert "## Adapter bridge status" in markdown
    assert "not OpenSSL leakage evidence" in markdown
    validate_openssl_derived_metadata_profile_report(markdown)


def test_profile_report_writes_markdown(tmp_path) -> None:
    summary = build_openssl_derived_metadata_profile_demo_chain(epochs=20)["demo_summary"]
    markdown = render_openssl_derived_metadata_profile_report(summary)
    path = tmp_path / "profile-demo-report.md"

    write_openssl_derived_metadata_profile_report(path, markdown)

    assert path.read_text(encoding="utf-8").startswith("# OpenSSL-Derived Metadata Profile Report")


def test_profile_report_rejects_malformed_markdown() -> None:
    with pytest.raises(OpenSSLDerivedMetadataProfileReportError, match="newline"):
        validate_openssl_derived_metadata_profile_report("# OpenSSL-Derived Metadata Profile Report")
