import logging

# Create a custom logger
logger = logging.getLogger('my_app')

# Set the log level
logger.setLevel(logging.DEBUG)

# Create file handler which logs messages to a file
file_handler = logging.FileHandler('./logs/server.log')
file_handler.setLevel(logging.DEBUG)  # Log only ERROR and above to the file

# Create console handler for displaying logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Log all levels to the console

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Log some messages - Syntax
# logger.debug("This is a debug message.")
# logger.info("This is an info message.")
# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.critical("This is a critical message.")

logger.info("Server restarted.")
