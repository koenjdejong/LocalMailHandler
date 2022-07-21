from src import app, mail_service, config

# Sent mail that the server has started
mail_service.send_email(config['mail']['recipient_email'], "Server started.",
'''Hello there!

I would hereby like to inform you that the LocalMailHandler has been started.

Kind regards,

Your friendly LocalMailHandler''')
app.logger.info("LocalMailHandler started and startup mail sent.")

# Start server
app.run(host='127.0.0.1', port=4650)
