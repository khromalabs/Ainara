# Ainara - Open Source AI Assistant Framework
# Copyright (C) 2025 Rubén Gómez http://www.khromalabs.org

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see
# <https://www.gnu.org/licenses/>.

import logging
from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""

    @abstractmethod
    def process_text(self, text: str, system_message: str = "") -> str:
        """Process text using the LLM backend"""
        pass


class LiteLLMBackend(LLMBackend):
    """LiteLLM implementation of LLM backend"""

    def __init__(self):
        import os

        # import litellm
        # litellm.set_verbose = True
        from litellm import completion

        # from litellm import completion, completion_cost

        self.completion = completion
        # self.completion_cost = completion_cost

        # Initialize provider dictionary and logger
        self.provider = {}
        self.logger = logging.getLogger(__name__)

        # Define environment variable mappings
        env_vars = {
            "model": ("AI_API_MODEL", True),  # (env_var_name, required)
            "api_base": ("OPENAI_API_BASE", False),
            "api_key": ("OPENAI_API_KEY", False),
        }

        self.logger.debug("Checking environment variables:")
        for key, (env_var, required) in env_vars.items():
            value = os.environ.get(env_var)
            self.logger.debug(
                f"{env_var}: {'[SET]' if value else '[MISSING]'}"
            )
            if required and not value:
                raise ValueError(
                    f"Missing required environment variable: {env_var}"
                )
            if value:  # Only add to provider if value exists
                self.provider[key] = value

    def my_custom_logging_fn(self, model_call_dict):
        self.logger.debug(f"LiteLLM: {model_call_dict}")

    def process_text(
        self,
        text: str,
        system_message: str = "",
        chat_history: list = None,
        stream: bool = False,
    ) -> str:
        """Process text using LiteLLM

        Args:
            text: The text to process
            system_message: Optional system message to prepend
            chat_history: Optional list of previous messages in
                          [user_msg, assistant_msg] pairs
            stream: Whether to stream the response
        """
        messages = [{"role": "system", "content": system_message}]

        # Add chat history if provided
        if chat_history:
            for i in range(0, len(chat_history), 2):
                messages.append({"role": "user", "content": chat_history[i]})
                if i + 1 < len(chat_history):
                    messages.append(
                        {"role": "assistant", "content": chat_history[i + 1]}
                    )

        # Add current message
        messages.append({"role": "user", "content": text})

        try:
            completion_kwargs = {
                "model": self.provider["model"],
                "messages": messages,
                "temperature": 0.2,
                "stream": stream,
                **(
                    {"api_base": self.provider["api_base"]}
                    if "api_base" in self.provider
                    else {}
                ),
                **(
                    {"api_key": self.provider["api_key"]}
                    if "api_key" in self.provider
                    else {}
                ),
                "logger_fn": self.my_custom_logging_fn,
            }

            self.logger.info(
                f"{__name__}.{self.__class__.__name__} Sending completion"
                " request..."
            )
            response = self.completion(**completion_kwargs)

            if stream:
                # For streaming, yield each chunk of text
                for chunk in response:
                    self.logger.debug(f"Stream chunk: {chunk}")
                    if hasattr(chunk.choices[0], "delta"):
                        content = chunk.choices[0].delta.content
                        if content is not None:
                            self.logger.debug(
                                f"Yielding delta content: {content}"
                            )
                            yield content
                    elif hasattr(chunk.choices[0], "text"):
                        self.logger.debug(
                            f"Yielding text: {chunk.choices[0].text}"
                        )
                        yield chunk.choices[0].text
            else:
                # For non-streaming, return complete response
                if hasattr(response.choices[0], "message"):
                    return response.choices[0].message.content.rstrip("\n")
                elif hasattr(response.choices[0], "text"):
                    return response.choices[0].text.rstrip("\n")
                else:
                    self.logger.error("Unexpected response format")
                    return ""

        except Exception as e:
            self.logger.error(
                f"Unable to get a response from the AI: {str(e)}"
            )
            return ""
