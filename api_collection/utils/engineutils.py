from flask import current_app as app


def get_engine_config(config_name, engine, lang, default=None):
    config = app.config[config_name]
    key1 = '{}_lang-{}'.format(engine, lang)
    key2 = engine
    if key1 in config:
        return config[key1]
    elif key2 in config:
        return config[key2]
    else:
        return default
