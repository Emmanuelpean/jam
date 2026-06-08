# Manual Testing

Follow the following steps to test the application manually.
Set test_mode=False in the .env file.

# Authentification
* [ ] Create a new account
  * [X] Errors show when submitting with empty fields
  * [X] Errors show when submitting with invalid email format
  * [X] Error clears when user submits valid data or checks the checkbox
  * [X] Error shows when user submits an incorrect password (password mismatch or too short)
  * [X] Error shows when user submits an input too long
  * [X] Error shows if user submits an already used email address
* [ ] Login
  * [ ] Login with correct credentials
  * [ ] Login with incorrect credentials
* [ ] Password reset

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
* [ ] Person creation with all fields filled in.
* [ ] Aggregator creation with all fields filled in.
* [ ] Keyword creation with all fields filled in.

# Table customisation
* [ ] Table can be sorted by any column.
* [ ] Table columns can be toggled
* [ ] Filters work