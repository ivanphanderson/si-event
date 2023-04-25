import requests

def get_sso_ui_data(username, password):
    return requests.post(
        'https://api.cs.ui.ac.id/authentication/ldap/v2/',
        data = {
            'username':username,
            'password':password
        }
    )