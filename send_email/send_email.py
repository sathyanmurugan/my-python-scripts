import io
import os
import smtplib
import mimetypes
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from bs4 import BeautifulSoup

def get_recipients_from_file(file):
    """ Returns list of recipients read from file. Every line must be one address. """
    with open(file, mode='r', encoding='utf-8') as fin:
        # Get only lines containing '@'
        recipients = [r.strip() for r in fin.readlines() if '@' in r]
    return recipients

def is_html(string):
    """ Returns True if BeautifulSoup finds a html tag in string """
    return bool(BeautifulSoup(string, 'html.parser').find())

def get_html_paragraph(string):
    """ Wraps string into HTML paragraph. If string is already HTML, html, head, body tags are
        removed. Otherwise, line breaks are replaced with <br/> tags to get correct layout in HTML.
    """
    # Set up new HTML
    soup = BeautifulSoup('', 'html.parser')
    # Add paragraph tag
    paragraph = soup.new_tag('p')
    # Read string as HTML
    html = BeautifulSoup(string, 'html.parser')
    # If string is HTML, clean it and append it to paragraph
    if html.find():
        # Remove html tag if present
        if html.html is not None:
            html.html.unwrap()
        # Remove head tag and its content if present
        if html.head is not None:
            html.head.decompose()
        # Remove body tag if present
        if html.body is not None:
            html.body.unwrap()
        paragraph.append(html)
    # If string is not HTML, replace line breaks with <br/> tag and append it to paragraph
    else:
        text = BeautifulSoup('<br/>'.join(string.splitlines()), 'html.parser')
        paragraph.append(text)
    # Append paragraph
    soup.append(paragraph)
    return soup

def get_html_message(message_parts):
    """ Transforms messsage_parts into one HTML string
    message_parts: List of strings
    """
    # Set up new HTML
    soup = BeautifulSoup('', 'html.parser')
    # Add html tag
    html = soup.new_tag('html')
    # Add all message parts as HTML to html tag
    for message in message_parts:
        html.append(get_html_paragraph(message))
    # Append html
    soup.append(html)
    # Return HTML as string
    return soup.prettify()

def get_plain_message(message_parts):
    """ Transforms messsage_parts into one plain text string
    message_parts: List of strings
    """
    # Join all strings separated by line break
    return '\n'.join(message_parts)

def df_to_html(df, *args, **kwargs):
    """ Converts a pandas DataFrame df to HTML, can be used to embed in email.
    Additional arguments to this function are passed through to pandas method to_html
    """
    table = io.StringIO()
    df.to_html(table, *args, **kwargs)
    html_table = table.getvalue()
    return html_table

def get_attachement(file):
    """ Returns MIME object from input file to be used as attachment for an email
        Adapted from https://docs.python.org/3.5/library/email-examples.html
    """
    # Guess the content type based on the file's extension
    ctype, encoding = mimetypes.guess_type(file)
    # No guess could be made or file is encoded (compressed), use a generic type
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    # Create MIME object according to type
    if maintype == 'text':
        with open(file) as fin:
            attachement = MIMEText(fin.read(), _subtype=subtype)
    elif maintype == 'image':
        with open(file, 'rb') as fin:
            attachement = MIMEImage(fin.read(), _subtype=subtype)
    elif maintype == 'audio':
        with open(file, 'rb') as fin:
            attachement = MIMEAudio(fin.read(), _subtype=subtype)
    else:
        with open(file, 'rb') as fin:
            attachement = MIMEBase(maintype, subtype)
            attachement.set_payload(fin.read())
        # Encode the payload using Base64
        encoders.encode_base64(attachement)
    # Set the filename parameter
    attachement.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
    return attachement

def send_gmail(email_address, app_password, recipients, subject, message_parts,
               realname='BI Python', attachments=None):
    """ Sends email via Gmail
    email_address: Gmail address from which the email should be sent
    app_password: Gmail app password, NOT the normal password used to login
        You can generate one at https://security.google.com/settings/security/apppasswords
    recipients: List of email addresses to which the email should be sent
    subject: Subject of email
    message_parts: List of strings for different parts in the email, e.g., plain text or html
        The function takes care to set the correct Content-Type. If any part is html, the
        resulting message will be in html format, otherwise, it will be plain text.
    realname: Name which is shown as sender of the email. Use None to shown none.
    attachments: List of files which are attached to the email
    """
    if attachments is None:
        attachments = []
    # Check if recipients is list/tuple
    if not isinstance(recipients, (list, tuple)):
        raise TypeError("Argument recipients must be a list/tuple.")
    # Check if message_parts is list/tuple
    if not isinstance(message_parts, (list, tuple)):
        raise TypeError("Argument message_parts must be a list/tuple.")
    # Check if attachments is list/tuple
    if not isinstance(attachments, (list, tuple)):
        raise TypeError("Argument attachments must be a list/tuple.")
    # Setup email
    email = MIMEMultipart()
    # Add recipients as comma separated string
    email['To'] = ', '.join(recipients)
    # Add real name and email address to 'From' field
    email['From'] = formataddr((realname, email_address))
    # Add subject
    email['Subject'] = subject
    # Format text according to type of parts in message_parts
    if any(is_html(msg) for msg in message_parts):
        text = MIMEText(get_html_message(message_parts), 'html')
    else:
        text = MIMEText(get_plain_message(message_parts), 'plain')
    # Add text to email
    email.attach(text)
    # Attach files to email
    for attachement in attachments:
        email.attach(get_attachement(attachement))
    # Login and send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_address, app_password)
        server.send_message(email)
