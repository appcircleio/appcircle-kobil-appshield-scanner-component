# Appcircle _KOBIL AppShield Scanner_ component for Android/iOS

Integration that allows testing security and app protection features, and determines whether an app contains security/defense mechanisms, using KOBIL Appshield Scanner API.

## Required Inputs

- `AC_APPSHIELD_APP_FILE_PATH`: App file URL or environment variable. URL to app file (apk/aab/ipa) or an environment variable representing its path.
- `AC_APPSHIELD_API_KEY` : API key required for using KOBIL Appshield Scanner API.

## Optional Inputs

- `AC_APPSHIELD_USER_MAIL`: User mail if user wants to get detailed test results in a PDF format.
- `AC_APPSHIELD_UPLOAD_TIMEOUT`: File upload timeout in seconds.

## Output Variables

- `AC_APPSHIELD_IS_APP_SECURE`: Booelan variable indicating whether the app is properly hardened and contains the security/defense mechanisms. "true" indicates app is secure, "false" indicates app is not completely secure (has missing security measures), and "null" indicates the testing has failed for some internal reason.

