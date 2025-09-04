from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any
from datetime import datetime
import json


@dataclass
class EmailSetup:
    """
    A class to structure the data for an email API POST request.

    Attributes:
        recipients (List[str]): A list of email addresses for recipients.
        subject (str): The subject line of the email.
        template_data (Dict[str, Any]): A dictionary of key-value pairs
                                        to fill placeholders in the email template.
        attachments (Dict[str, str]): A dictionary where keys are filenames and
                                      values are file paths to attach.
        body_images (Dict[str, str]): A dictionary where keys are Content-ID (CID)
                                      for embedded images and values are file paths.
    """
    recipients: List[str]
    subject: str

    # Use a dictionary to hold all key-value pairs for the template
    template_data: Dict[str, Any] = field(default_factory=dict)

    # Use dictionaries for attachments and embedded images
    attachments: Dict[str, str] = field(default_factory=dict)
    body_images: Dict[str, str] = field(default_factory=dict)

    def to_api_payload(self) -> Dict[str, Any]:
        """
        Combines all class attributes into a single dictionary
        for use as an API request body.

        This method merges `template_data` directly into the final dictionary
        to match the desired flat structure for the API call.
        """
        payload = asdict(self)

        # Merge template_data directly into the main dictionary
        if 'template_data' in payload:
            template_data = payload.pop('template_data')
            payload.update(template_data)

        return payload
