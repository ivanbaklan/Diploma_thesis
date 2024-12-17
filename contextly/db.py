# Data Base config
TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    # "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "models": {
            "models": [
                "contextly.models.user",
                "contextly.models.video",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}
