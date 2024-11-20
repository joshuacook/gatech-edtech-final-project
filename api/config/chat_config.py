import os
from functools import partial
from typing import Union, Type

import openai
from anthropic import Anthropic, AnthropicBedrock

# Client configurations
ANTHROPIC_SONNET_CLIENT = partial(Anthropic, model="claude-3-5-sonnet-latest")
ANTHROPIC_BEDROCK_CLIENT = partial(
    AnthropicBedrock,
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    aws_access_key=os.getenv("aws_access_key_id"),
    aws_secret_key=os.getenv("aws_secret_access_key"),
)

# Default client
CURRENT_CLIENT = openai

# Type alias for client types
ChatClient = Union[Type[openai], partial[Union[Anthropic, AnthropicBedrock]]]
