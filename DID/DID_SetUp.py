"""Model for DIDSet transaction type."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional, Pattern

from typing_extensions import Final

from xrpl.models.transactions.transaction import Transaction
from xrpl.models.transactions.types import TransactionType
from xrpl.models.utils import require_kwargs_on_init

# Compile a regex for matching hexadecimal strings.
HEX_REGEX: Final[Pattern[str]] = re.compile(r"[a-fA-F0-9]+")

@require_kwargs_on_init
@dataclass(frozen=True)
class DIDSet(Transaction):
    """
    Represents a DIDSet transaction on the XRP Ledger, 
    used for creating or updating Distributed Identifiers (DIDs).

    Attributes:
        did_document (Optional[str]): A hexadecimal string representing the DID document.
        data (Optional[str]): Additional data related to the DID, in hexadecimal format.
        uri (Optional[str]): A URI pointing to the DID document or related information.
        transaction_type (TransactionType): The type of transaction, fixed to DID_SET.

    Note: At least one of did_document, data, or uri must be provided.
    """

    did_document: Optional[str] = None
    data: Optional[str] = None
    uri: Optional[str] = None

    transaction_type: TransactionType = field(
        default=TransactionType.DID_SET,
        init=False,
    )

    def _get_errors(self) -> Dict[str, str]:
        """
        Validates the transaction fields, ensuring compliance with the XRP Ledger requirements.

        Returns:
            Dict[str, str]: A dictionary of errors found during validation, if any.
        """
        errors = super()._get_errors()

        # Check if at least one DID-related field is provided
        if self.did_document is None and self.data is None and self.uri is None:
            errors["did_set"] = "Must have one of `did_document`, `data`, and `uri`."

        # Validate the format and length of the fields
        def _process_field(name: str, value: Optional[str]) -> None:
            if value is not None:
                error_strs = []
                if not HEX_REGEX.fullmatch(value):
                    error_strs.append("must be hex")
                if len(value) > 256:
                    error_strs.append("must be <= 256 characters")
                if error_strs:
                    errors[name] = (" and ".join(error_strs) + ".").capitalize()

        _process_field("did_document", self.did_document)
        _process_field("data", self.data)
        _process_field("uri", self.uri)

        return errors


