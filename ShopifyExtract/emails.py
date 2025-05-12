import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_failure_email(subject, body, to_email, from_email, smtp_server, smtp_port, login, password):
    """
    Sends a failure email with the given subject and body.

    :param subject: Subject of the email
    :param body: Body of the email
    :param to_email: Recipient email address
    :param from_email: Sender email address
    :param smtp_server: SMTP server address
    :param smtp_port: SMTP server port
    :param login: SMTP login username
    :param password: SMTP login password
    """
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(login, password)
            server.send_message(msg)
        print("Failure email sent successfully.")
    except Exception as e:
        print(f"Error sending failure email: {e}")