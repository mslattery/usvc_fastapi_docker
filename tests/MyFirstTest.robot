*** Settings ***
Documentation     A UI test suite that verifies a login token is set as a cookie.
Library           Browser
Suite Setup       New Browser    browser=${BROWSER}    headless=${HEADLESS}
Test Setup        New Page    url=${BASE_URL}
Test Teardown     Close Context
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}       http://localhost:8989
${BROWSER}        chromium
${HEADLESS}       False

*** Test Cases ***
Scenario: User can log in and receive an access_token cookie
    [Tags]    ui    auth    cookie
    Verify Home Page Is Open
    Click The Mock Login Link
    Verify Token Cookie Is Set

*** Keywords ***
Verify Home Page Is Open
    # Waits for an element with the text "Login with Mock Service" to be visible
    Wait For Elements State    text="Login with Mock Service"    visible

Click The Mock Login Link
    # The standard Click keyword is all we need. It will wait for navigation
    # to complete, by which time the browser will have processed the Set-Cookie header.
    Click    xpath=//a[contains(@href, '/auth/login?provider=mock')]

Verify Token Cookie Is Set
    ${cookies}=    Get Cookies
    Log To Console    \n--- Browser Cookies Found ---\n${cookies}

    ${access_token_cookie}=    Set Variable    ${None}
    FOR    ${cookie}    IN    @{cookies}
        IF    '${cookie['name']}' == 'access_token'
            ${access_token_cookie}=    Set Variable    ${cookie}
            BREAK
        END
    END

    Should Not Be Equal    ${access_token_cookie}    ${None}    msg=Cookie with name 'access_token' was not found.

    # --- THE FIX IS HERE ---
    # Use extended variable syntax to directly access the 'value' from the cookie dictionary.
    Should Not Be Empty    ${access_token_cookie['value']}

    Log To Console    SUCCESS: Found 'access_token' cookie.