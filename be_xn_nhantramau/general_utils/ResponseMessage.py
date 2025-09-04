import glob
import os
import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Any, Callable, TypeVar

# A type variable to represent any type that can be returned by a message retrieval function.
T = TypeVar('T')


class MessageType(Enum):
    """
    Enumerates the different types of messages.
    """
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class Message:
    """
    Represents a single message entry with a unique key and its translations.
    """
    key: str
    text: Dict[str, str]


class MessageManager:
    """
    Manages the loading and retrieval of all application messages.
    Loads messages from JSON files once and caches them for efficient access.
    """
    _instance = None
    _MESSAGES_DATA_CACHE: Dict[str, Message] = {}
    _is_loaded = False

    def __new__(cls, directory_path: str):
        """
        Ensures only one instance of the MessageManager is created (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(MessageManager, cls).__new__(cls)
            cls._instance._load_messages(directory_path)
        return cls._instance

    def _find_json_files(self, directory_path: str) -> list[str]:
        """
        Finds and returns a list of all .json file paths in a given directory.
        """
        search_pattern = os.path.join(directory_path, '*.json')
        json_files = glob.glob(search_pattern)
        return json_files

    def _combine_json_files(self, file_paths: list[str]) -> list[Dict[str, Any]]:
        """
        Reads and combines the content of multiple JSON files into a single list.
        """
        combined_data = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        combined_data.extend(data)
                    else:
                        combined_data.append(data)
            except json.JSONDecodeError:
                print(
                    f"Error: Could not decode JSON from '{file_path}'. Skipping.")
            except IOError:
                print(f"Error: Could not read file '{file_path}'. Skipping.")
        return combined_data

    def _load_messages(self, directory_path: str):
        """
        Loads and processes message data from all JSON files in the specified directory.
        The data is converted into a dictionary keyed by message key for fast lookup.
        """
        if self._is_loaded:
            return

        found_files = self._find_json_files(directory_path)
        all_messages_list = self._combine_json_files(found_files)

        # Correctly handles the user's provided JSON structure (a single dictionary)
        for data_dict in all_messages_list:
            if isinstance(data_dict, dict):
                for key, translations in data_dict.items():
                    if isinstance(translations, dict):
                        self._MESSAGES_DATA_CACHE[key] = Message(
                            key=key,
                            text=translations
                        )

        self._is_loaded = True

    def get_response_message(self, key: str, lang: str = 'vn') -> str:
        """
        Retrieves a localized message from the cached messages data using a key.

        Args:
            key (str): The unique key for the message.
            lang (str): The language code for the desired message (e.g., 'en', 'vn').

        Returns:
            str: The localized message string, or a fallback message if not found.
        """
        message_entry = self._MESSAGES_DATA_CACHE.get(key)
        if not message_entry:
            return f"Không tìm thấy key '{key}'."

        # Now, try to get the message for the specified language.
        # Use 'vn' as a fallback if the requested language isn't available.
        return message_entry.text.get(lang, message_entry.text.get('vn', f"Message for key '{key}' not available in any language."))


# -- Declare -- #
target_path = 'general_utils/Message/'


def MESSAGE_INSTANCES(key, language):
    manager = MessageManager(target_path)
    return manager.get_response_message(key, lang=language)
