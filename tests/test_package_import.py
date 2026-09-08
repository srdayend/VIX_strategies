def test_package_imports_with_installed_pandas_version():
    import vix_strategies

    assert vix_strategies.__all__ == []
