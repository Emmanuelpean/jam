# Manual Testing

Follow the following steps to test the application manually.
Set test_mode=False in the .env file.

# Authentification
* [X] Create a new account
  * [X] Errors show when submitting with empty fields
  * [X] Errors show when submitting with invalid email format
  * [X] Error clears when user submits valid data or checks the checkbox
  * [X] Error shows when user submits an incorrect password (password mismatch or too short)
  * [X] Error shows when user submits an input too long
  * [X] Error shows if user submits an already used email address
* [X] Login
  * [X] Login with correct credentials
  * [X] Login with incorrect credentials
* [X] Password reset

# Homepage
* [X] Welcome modal shows on first visit.
* [X] Tour popup shows after the welcome modal is closed.
* [X] All tours are working.

# Jobs
* [X] Job creation with all fields filled in.
* [X] Add interview
* [X] Add update

# Other data
* [X] Company creation with all fields filled in.
* [X] Person creation with all fields filled in.
* [X] Aggregator creation with all fields filled in.
* [X] Keyword creation with all fields filled in.

# Table customisation
* [X] Table can be sorted by any column.
* [X] Table columns can be toggled
* [X] Filters work

# Premium
* [ ] Can activate premium
* [ ] Can deactivate premium