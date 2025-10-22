# Appcircle _AppShield Scanner_ component for Android/iOS

Integration that allows testing security and app protection features, and determines whether an app contains security/defense mechanisms,
using Appshield Scanner API.

## Required Inputs

- `AC_APPSHIELD_APP_FILE_PATH`: App file URL or environment variable. URL to app file (apk/aab/ipa) or an environment variable representing its path (i.e. $AC_APK_PATH or $AC_AAB_PATH)
- `AC_APPSHIELD_USER_MAIL`: (Optional) User mail if user wants to get detailed test results in a PDF format.

## Output Variables

- `AC_APPSHIELD_IS_APP_SECURE`: Booelan variable indicating whether the app is properly hardened and contains the security/defense mechanisms. 
    "true" indicates app is secure, "false" indicates app is not completely secure (has missing security measures), and "null" indicates the testing 
    has failed for some internal reason.

