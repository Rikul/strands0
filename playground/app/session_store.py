"""Session state persistence for Strands Playground."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def validate_user_id(user_id: str) -> bool:
    """Validate user_id to prevent path traversal attacks."""
    if not user_id:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]+$", user_id))


@dataclass
class SessionStore:
    table_name: str | None
    table_region: str | None
    primary_key: str | None

    def load_messages(self, user_id: str) -> list:
        if not validate_user_id(user_id):
            raise ValueError("Invalid user_id: must contain only alphanumeric characters, underscores, or hyphens")

        if not self.table_name and not self.table_region:
            # Local file sessions
            try:
                with open(f"sessions/{user_id}.json", "r") as f:
                    state = json.load(f)
                    return state.get("messages", [])
            except FileNotFoundError:
                return []

        # DynamoDB sessions
        try:
            if not (self.table_name and self.table_region and self.primary_key):
                return []

            dynamodb = boto3.resource("dynamodb", region_name=self.table_region)
            table = dynamodb.Table(self.table_name)
            response = table.get_item(Key={self.primary_key: user_id})
            if "Item" in response:
                return response["Item"].get("messages", [])
            return []
        except Exception as e:
            logger.error(f"Failed to restore session from DynamoDB: {e}")
            return []

    def save_messages(self, user_id: str, messages: list) -> None:
        if not validate_user_id(user_id):
            raise ValueError("Invalid user_id: must contain only alphanumeric characters, underscores, or hyphens")

        if not self.table_name and not self.table_region:
            os.makedirs("sessions", exist_ok=True)
            with open(f"sessions/{user_id}.json", "w") as f:
                json.dump({"messages": messages}, f)
            return

        try:
            if not (self.table_name and self.table_region and self.primary_key):
                return

            dynamodb = boto3.resource("dynamodb", region_name=self.table_region)
            table = dynamodb.Table(self.table_name)
            table.put_item(Item={self.primary_key: user_id, "messages": messages})
        except ClientError as e:
            logger.error(f"Failed to save session to DynamoDB: {e}")
