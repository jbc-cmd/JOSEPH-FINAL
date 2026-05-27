import os
import subprocess
import sys


def run(command):
    print(f"Running: {' '.join(command)}")
    subprocess.check_call(command)


def main():
    python = sys.executable

    run([python, "manage.py", "collectstatic", "--noinput"])
    run([python, "manage.py", "migrate", "--noinput"])
    run([python, "manage.py", "init_data"])

    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if admin_username and admin_email and admin_password:
        run([
            python,
            "manage.py",
            "create_admin_account",
            "--username",
            admin_username,
            "--email",
            admin_email,
            "--password",
            admin_password,
        ])
    else:
        print("Skipping admin account creation because ADMIN_USERNAME, ADMIN_EMAIL, or ADMIN_PASSWORD is missing.")


if __name__ == "__main__":
    main()
