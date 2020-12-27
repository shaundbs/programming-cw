import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


class Emails:
    def registration_email(recipient, firstName, lastName, accountType):

        sender_email = "gowerstsurgery.adm@gmail.com"
        admin = sender_email
        password = "19_Healthcare_97"

        rec = recipient

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Registration Confirmation"
        msg['From'] = admin
        msg['To'] = rec

        # Create the body of the message.
        text = "Hi " + firstName + " " + lastName + " thank you for registering with Gower St. Surgery" \
               "the e-health management service.\n \n Your account has been successfully set up with " + accountType \
               + " " \
               "priviledges. You can 1. Login \n 2. Book appointments \n 3. Reschedule appointments \n" \
               "4. Cancel appointments \n 5. Book a session with one of our external specialists \n" \
               " \n \n Log back into the application begin </p>\n "

        html = """\
        <html lang="en">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <title>Register as a new patient/GP</title>
        </head>
        <body bgcolor="#EBEBEB" link="#B64926" vlink="#FFB03B">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#EBEBEB">
        <tr>
        <td>
        <table width="600" align="center" border="0" cellpadding="0" cellspacing="0" bgcolor="#FFFFFF">
        <tr>
        <td style="padding-top: 0.5em">
        <h1 style="font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, sans-serif; color: #0E618C; text-align:
        center">Welcome to Gower St. Surgery<br>--e-health management service--<br></h1>
        </td>
        </tr>
        <tr>
        <td align="center">
        <img src="cid:image1" alt="Logo" style="width:225px;height:200px;"><br>
        </td>
        </tr>
        <tr>
        <td style="font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, sans-serif; color: #1B1B1B;
         font-size: 14px; padding: 1em">
        </td>
        </tr>
        <tr>
        <td style="font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, sans-serif; color: #1b1b1b; 
        font-size: 14px; padding: 1em">
        <p>Hi <b>""" + str(firstName) + """  """ + str(lastName) + """</b>, thank you for registering with Gower St. Surgery,
        the e-health management service. <br><br>
        Your account has been successfully set up with <b>""" + str(accountType) + """</b> privileges. You can: <br><br>
        1. Login <br>
        2. Book appointments <br>
        3. Reschedule appointments <br>
        4. Cancel appointments <br>
        5. Book a session with one of our external specialists <br><br> Log back into the application to begin </p>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </table>
        </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # This example assumes the image is in the current directory
        fp = open('logo.png', 'rb')
        msgimage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msgimage.add_header('Content-ID', '<image1>')
        msg.attach(msgimage)

        # Send the message via local SMTP server.
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender_email, password)
        mail.sendmail(admin, rec, msg.as_string())
        mail.quit()

    def appointment_confirmation_email(recipient, firstName, lastName, accountType):
        sender_email = "gowerstsurgery.adm@gmail.com"
        admin = sender_email
        password = "19_Healthcare_97"

        rec = recipient

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Registration Confirmation"
        msg['From'] = admin
        msg['To'] = rec

        # Create the body of the message.
        text = "Hi " + firstName + " " + lastName + " thank you for registering with Gower St. Surgery" \
                "the e-health management service.\n \n Your account has been successfully set up with " + accountType \
               + " " \
                 "priviledges. You can 1. Login \n 2. Book appointments \n 3. Reschedule appointments \n" \
                 "4. Cancel appointments \n 5. Book a session with one of our external specialists \n" \
                 " \n \n Log back into the application begin </p>\n "

        html = """\
        <html lang="en">
        <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
            <title>Register as a new patient/GP</title>
        </head>
        <body bgcolor="#EBEBEB" link="#B64926" vlink="#FFB03B">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#EBEBEB">
        <tr>
        <td>
        <table width="600" align="center" border="0" cellpadding="0" cellspacing="0" bgcolor="#FFFFFF">
        <tr>
        <td style="padding-top: 0.5em">
        <h1 style="font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, sans-serif; color: #0E618C; text-align:
        center">Welcome to Gower St. Surgery<br>--e-health management service--<br></h1>
        </td>
        </tr>
        <tr>
        <td align="center">
        <img src="cid:image1" alt="Logo" style="width:225px;height:200px;"><br>
        </td>
        </tr>
        <tr>
        <td style="font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, sans-serif; color: #1B1B1B;
         font-size: 14px; padding: 1em">
        </td>
        </tr>
        <tr>
        <td style="font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, sans-serif; color: #1b1b1b; 
        font-size: 14px; padding: 1em">
        <p>Hi <b>""" + str(firstName) + """  """ + str(lastName) + """</b>, thank you for registering with Gower St. Surgery,
        the e-health management service. <br><br>
        Your account has been successfully set up with <b>""" + str(accountType) + """</b> privileges. You can: <br><br>
        1. Login <br>
        2. Book appointments <br>
        3. Reschedule appointments <br>
        4. Cancel appointments <br>
        5. Book a session with one of our external specialists <br><br> Log back into the application begin </p>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </table>
        </body>
        </html>
        """

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # This example assumes the image is in the current directory
        fp = open('logo.png', 'rb')
        msgimage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msgimage.add_header('Content-ID', '<image1>')
        msg.attach(msgimage)

        # Send the message via local SMTP server.
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender_email, password)
        mail.sendmail(admin, rec, msg.as_string())
        mail.quit()

