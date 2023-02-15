from loguru import logger

logger.add('logger.log', 
	format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}', 
	level = 'DEBUG', 
	rotation = '1 week', 
	compression = 'zip'
)