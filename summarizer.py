from llm_helper import LlmHelper
from ollama import chat
from ollama import ChatResponse

class Summarizer:
    def __init__(self):
        self.prompt = """Everything that is written after this message has to be summarized
            
            Summarize the following text:
        """
        pass

    def summarize(self, text):
        llm_helper = LlmHelper()

        return llm_helper.get_response([{"role": "user", "content": self.prompt + text}])

    def summarize_using_ollama(self, text):

        response: ChatResponse = chat(model='qwen3:4b', messages=[
            {
                'role': 'user',
                'content': self.prompt + text,
            },
        ])
        return response.message.content