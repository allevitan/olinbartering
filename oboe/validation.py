#validation.py

def passwordErrors(passwords):
	errors = set()
	for password in passwords:
		if len(password) <= 6:
			errors.add('Passwords must contain at least 6 characters long.')
		if len(password) >= 30:
			errors.add('Passwords must be less than 30 characters.')

