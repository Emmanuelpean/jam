# Manual Testing

Follow the following steps to test the application manually.
Set test_mode=False in the .env file.

# Authentification
* [ ] Create a new account
  * [ ] Errors show when submitting with empty fields
  * [ ] Errors show when submitting with invalid email format
  * [ ] Error clears when user submits valid data or checks the checkbox
  * [ ] Error shows when user submits an incorrect password (password mismatch or too short)
  * [ ] Error shows when user submits an input too long
  * [ ] Error shows if user submits an already used email address