import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


class Emails:
    @staticmethod
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
        text = "Hi " + firstName + " " + lastName + " thank you for registering with Gower St. Surgery." \
        "Please await confirmation of your registration from one of our admins/GPs and once confirmed you will be able "
        "to log back into the application and manage your healthcare with us"

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
        Please await confirmation of your registration from one of our admins/GPs and once confirmed you will be able
        to log back into the application and manage your healthcare with us.</p>
        </td>
        </tr>
        </table>
        </td>
        </tr>
        </table>
        </body>
        </html>
        """

        #text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container
        msg.attach(part1)
        msg.attach(part2)

        fp = open('logo.png', 'rb')
        msgimage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID
        msgimage.add_header('Content-ID', '<image1>')
        msg.attach(msgimage)

        # Send the message
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender_email, password)
        mail.sendmail(admin, rec, msg.as_string())
        mail.quit()
