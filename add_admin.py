from user_management import add_user

# Add admin user
username = "egymass"
password = "asd123"
user_type = "مدير"

success = add_user(username, password, user_type)
if success:
    print("Admin account created successfully!")
else:
    print("Failed to create admin account.")
