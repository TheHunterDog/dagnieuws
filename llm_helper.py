from transformers import AutoTokenizer, AutoModelForCausalLM


class LlmHelper:
    def __init__(self):
        self.llm_name = "Qwen/Qwen3-4B"
        self.tokenizer = None
        self.model = None

    def get_llm_name(self):
        return self.llm_name

    def __load_llm__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.llm_name,
            torch_dtype="auto",
            device_map="auto"
        )

    def get_response(self, messages=None):
        if messages is None:
            messages = [{"role": "user", "content": "Hi how are you"}]
        self.__load_llm__()
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True  # Switches between thinking and non-thinking modes. Default is True.
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        # conduct text completion
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=32768
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = self.tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        print("thinking content:", thinking_content)
        print("content:", content)

        self.__unload_llm__()

        return content

    def __unload_llm__(self):
        self.llm = None
