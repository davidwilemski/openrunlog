# COPY THIS TO orl_settings.py
class ORLSettings(object):
    """
    Open Run Log settings class

    This is instantiated on application.config
    """
    debug = True #change to False for production

    # change to correct values:
    db_name = 'orl_test' 
    db_host = 'localhost'
    db_port = 2117
    db_username = 'orl'
    db_password = 'orlpassword'

    cookie_secret = 'create_your_own_here'
