"""
ReflexionOS — Amazon Nova 2 Lite via AWS Bedrock
"""
from __future__ import annotations
import json
import re
from typing import Any

from .base import BaseProvider

# Inference profile ARN for Amazon Nova Lite v2
# Must use inference profile, not raw model ID
NOVA_LITE_PROFILE = "us.amazon.nova-lite-v1:0"


class BedrockNovaProvider(BaseProvider):
    """
    Calls Amazon Nova 2 Lite via AWS Bedrock Runtime using the
    converse API with inference profile.
    """

    def __init__(self, region: str = "us-east-1") -> None:
        try:
            import boto3  # type: ignore
        except ImportError as e:
            raise RuntimeError("boto3 is required: pip install boto3") from e

        self._client = boto3.client("bedrock-runtime", region_name=region)
        self._region = region

    @property
    def name(self) -> str:
        return "bedrock-nova-lite"

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Invoke Amazon Nova via Bedrock converse API.
        System prompt is folded into the user message since Nova Lite
        processes them together for best JSON adherence.
        """
        combined_prompt = (
            f"{system_prompt}\n\n"
            "IMPORTANT: Respond ONLY with valid JSON. No markdown fences. No preamble.\n\n"
            f"{user_prompt}"
        )

        body: dict[str, Any] = {
            "inferenceConfig": {
                "temperature": temperature,
                "maxTokens": 4096,
            },
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": combined_prompt}],
                }
            ],
        }

        try:
            response = self._client.converse(
                modelId=NOVA_LITE_PROFILE,
                **body,
            )
        except Exception as e:
            raise RuntimeError(f"Bedrock invocation failed: {e}") from e

        # Extract text from response
        raw = self._extract_text(response)
        return self._parse_json(raw)

    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(response: dict[str, Any]) -> str:
        """Pull the assistant text from a Bedrock converse response."""
        try:
            output = response["output"]["message"]["content"]
            texts = [block["text"] for block in output if "text" in block]
            return "\n".join(texts).strip()
        except (KeyError, TypeError) as e:
            raise ValueError(f"Unexpected Bedrock response shape: {e}") from e

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """
        Parse JSON from model output, stripping markdown fences if present.
        """
        # Strip ```json ... ``` or ``` ... ``` fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Model did not return valid JSON.\nRaw output:\n{raw[:500]}\nError: {e}"
            ) from e
