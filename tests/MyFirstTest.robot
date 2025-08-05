*** Settings ***
Documentation    A UI test suite for a simple FastAPI application using Selenium.
Library          SeleniumLibrary

*** Variables ***
${BASE_URL}      http://localhost:8000
${BROWSER}       edge

*** Test Cases ***
Scenario: User can log in by clicking the link
    [Tags]    ui    auth
    Open Browser To Home Page
    Click The Mock Login Link
    Verify Token Is Displayed On Page
    [Teardown]    Close Browser

*** Keywords ***
Open Browser To Home Page
    Open Browser    ${BASE_URL}    ${BROWSER}
    Wait Until Page Contains    Login with Mock
    Title Should Be    FastAPI UI Test

Click The Mock Login Link
    Click Link    xpath=//a[contains(@href, '/auth/login?provider=mock')]

Verify Token Is Displayed On Page
    Wait Until Page Contains    Your Token
    ${token_text}=    Get Text    id=token
    # This keyword just checks that the token element is not empty.
    Should Not Be Empty    ${token_text}
    Log To Console    Found Token: ${token_text}
