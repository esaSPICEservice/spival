from smtplib import SMTP        # use this for standard SMTP protocol   (port 25, no encryption)
from email.mime.text import MIMEText
import socket
import os
import json
import traceback


def send_status_email(config, body_text='', error=False):
    with open(config) as f:
        try:
            config = json.load(f)
        except:
            error_message = str(traceback.format_exc())
            print("Error: The SPIVAL JSON configuration file has syntactical errors.")
            print(error_message)
            raise

        SMTPserver = 'smtp.sciops.esa.int'
        sender = 'esa_spice@sciops.esa.int'

        destination = config['email'][0]['developer']

        USERNAME = "esa_spice"
        PASSWORD = "WRUBTNBLOJMHLUOR"

        # typical values for text_subtype are plain, html, xml
        text_subtype = 'html'

        try:
            # Prepare email message
            msg = MIMEText(body_text, text_subtype)
            if 'FAIL' in msg.as_string():
                error = True
            if error:
                subject = "[SPIVAL]: {} Tests FAIL".format(config['email'][0]['mission'])
            else:
                subject = "[SPIVAL]: {} Tests OK".format(config['email'][0]['mission'])
            msg['Subject'] = subject
            msg['From'] = sender  # some SMTP servers will do this automatically, not all

            # For each email in destination separated by ';' send the email
            dest_emails = destination.split(';')

            for dest_email in dest_emails:

                if "@" not in dest_email:
                    # Ignore invalid emails
                    continue

                conn = SMTP(SMTPserver)

                conn.starttls()
                conn.ehlo()

                # Pretend the SMTP server supports some forms of authentication.
                conn.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'

                conn.set_debuglevel(False)
                conn.login(USERNAME, PASSWORD)
                try:
                    conn.sendmail(sender, dest_email, msg.as_string() + '\n\n' + config['email'][0]['report'])
                except Exception as exc:
                    print("Send mail failed; {}".format(str(exc)))  # give a error message
                finally:
                    conn.quit()

            return msg.as_string()  # Just for testing purposes

        except Exception as exc:

            print("Mail failed; {}".format(str(exc)))  # give a error message
            return ""  # Just for testing purposes

