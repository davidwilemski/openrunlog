# COPY THIS TO orl_settings.py
class ORLSettings(object):
    """
    Open Run Log settings class

    This is instantiated on application.config
    """
    debug = True #change to False for production

    # change to correct values:
    db_name = 'openrunlog'
    db_uri = 'mongodb://localhost/openrunlog'

    cookie_secret = 'create_your_own_here'
