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

