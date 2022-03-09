# Command prefix
COMMAND_PREFIX = "s!"

# Location of secrets.json where the discord bot token is located.
SECRETS_FILE = "secrets.json"

# Logging format
LOGGING_FORMAT = "(%(asctime)s) [%(levelname)s] - %(message)s"

# Cogs in use
ACTIVE_COGS = [
    "cogs.core",
    "cogs.economy",
    "cogs.income",
]

ACTIVE_OBJECTS = [
    "objects.economy.account",
    "objects.stocks.stock",
]

ACTIVE_SEEDERS = [
    "objects.seeders.stocks"
]

# Data sources stocks
YAHOO_STOCKS = ["AAPL","MSFT","AMZN","FB","GOOGL","TSLA","NVDA","V"]
