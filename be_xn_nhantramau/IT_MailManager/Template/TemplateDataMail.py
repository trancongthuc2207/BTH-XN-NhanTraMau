class SendEmailDataSetup:
    """
    A class to encapsulate and manage data for a single email.
    """

    def __init__(self, subject: str, html_content: str):
        """
        Initializes the email data with a subject and HTML content.

        :param subject: The subject line of the email.
        :param html_content: The HTML body of the email.
        """
        self.recipients = []
        self.subject = subject
        self.html_content = html_content
        self.attachments = {}
        self.body_images = {}

    def add_recipient(self, email: str):
        """Adds a single recipient to the email."""
        self.recipients.append(email)

    def add_recipients(self, emails: list):
        """Adds a list of recipients to the email."""
        self.recipients.extend(emails)

    def add_attachment(self, filename: str, filepath: str):
        """
        Adds a file to be sent as an attachment.

        :param filename: The name of the file to display in the email.
        :param filepath: The local path to the file.
        """
        self.attachments[filename] = filepath

    def add_body_image(self, cid: str, filepath: str):
        """
        Adds an image to be embedded in the email body.

        :param cid: The Content-ID to reference the image in the HTML (e.g., 'cid:logo_image').
        :param filepath: The local path to the image file.
        """
        self.body_images[cid] = filepath

    def get_data(self) -> dict:
        """
        Returns a dictionary of all email data, ready to be passed
        to an email-sending function.
        """
        return {
            'recipients': self.recipients,
            'subject': self.subject,
            'html_content': self.html_content,
            'attachments': self.attachments,
            'body_images': self.body_images
        }
