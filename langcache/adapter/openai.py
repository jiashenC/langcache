import openai
from ..core import Cache

class LangCacheCompletions(openai.resources.chat.completions.Completions):
    # TODO: Add remaining args
    def create(self, messages, model):
        # Get the last message with role "user"
        last_user_message = [message for message in messages if message["role"] == "user"][-1]["content"]
        cached_value = self._client.cache.get(last_user_message)

        if cached_value is None:
            llm_output = openai.resources.chat.completions.Completions.create(self, messages=messages, model=model).choices[0].message.content
            self._client.cache.put(last_user_message, llm_output)
            return llm_output
        else:
            return cached_value


class OpenAI(openai.OpenAI):
    # TODO: Add remaining args
    def __init__(self, cache):
        super(OpenAI, self).__init__()
        self.cache = cache
        self.chat.completions = LangCacheCompletions(self)
