import main

# export AC_ENV_FILE_PATH=.env

##########################   Happy flows   ##########################

def test_is_app_secure_true_aab():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./secure_file.aab",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is True

def test_is_app_secure_true_ipa():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./secure_file.ipa",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is True

def test_is_app_secure_false_aab():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./not_secure_file.aab",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is False

def test_is_app_secure_false_apk():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./not_secure_file.apk",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is False

##########################   Exception Cases   ##########################

# Also, invalid file extension case
def test_is_app_secure_null():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./invalid_extension_file.zip",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is None

# Invalid file path case
def test_invalid_file_path():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./invalid_file_path.apk",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is None

# Invalid mail format case
def test_invalid_email_format():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./secure_file.aab",
        user_email="invalidmailformat",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is None

# Invalid API key case
def test_invalid_api_key():
    result = main.run_scanner(
        upload_timeout=300,
        file_path="./secure_file.aab",
        user_email="test@mail.com",
        api_key="wrong-api-key"
    )

    assert result is None

# Timeout exception case
def test_timeout_case():
    result = main.run_scanner(
        upload_timeout=1,
        file_path="./secure_file.aab",
        user_email="test@mail.com",
        api_key="f8b36d6f-7220-4fb5-8ad2-70a9a9dd2da6"
    )

    assert result is None

