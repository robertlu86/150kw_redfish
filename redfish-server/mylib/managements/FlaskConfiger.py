from flask import Flask

class FlaskConfiger:
    """Config global Flask app settings
    """

    # helper function
    @staticmethod
    def disable_strict_slashes_for_all_urls(app: Flask, matched_url_prefix: str):
        """
        Disable strict slashes for all rules that start with the matched URL prefix.
        ex: /redfish/v1/Chassis/1 allows /redfish/v1/Chassis/1/ 
        :param app: Flask app
        :param matched_url_prefix: URL prefix to match. ex: "/redfish/v1"
        """
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith(matched_url_prefix):
                rule.strict_slashes = False

    