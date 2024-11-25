import pprint
import urllib.parse
import json5
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

# Step 1 (Optional): Add a custom tool named `my_image_gen`.
@register_tool('my_image_gen')
class MyImageGen(BaseTool):
    # The `description` tells the agent the functionality of this tool.
    description = 'AI painting (image generation) service, input text description, and return the image URL drawn based on text information.'
    # The `parameters` tell the agent what input parameters the tool has.
    parameters = [{
        'name': 'prompt',
        'type': 'string',
        'description': 'Detailed description of the desired image content, in English',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        # `params` are the arguments generated by the LLM agent.
        prompt = json5.loads(params)['prompt']
        prompt = urllib.parse.quote(prompt)
        return json5.dumps(
            {'image_url': f'https://image.pollinations.ai/prompt/{prompt}'},
            ensure_ascii=False)


# Step 2: Configure the LLM you are using.
llm_cfg = {
    # Use the model service provided by DashScope:
    #'model': 'qwen-max',
    #'model_server': 'dashscope',
    # 'api_key': 'YOUR_DASHSCOPE_API_KEY',
    # It will use the `DASHSCOPE_API_KEY' environment variable if 'api_key' is not set here.

    # Use a model service compatible with the OpenAI API, such as vLLM or Ollama:
     'model': 'qwen2.5-code',
     'model_server': 'http://localhost:8000/v1',  # base_url, also known as api_base
     'api_key': 'EMPTY',

    # (Optional) LLM hyperparameters for generation:
    'generate_cfg': {
        'top_p': 0.8
    }
}

# Step 3: Create an agent. Here we use the `Assistant` agent as an example, which is capable of using tools and reading files.
system_instruction = '''You are a helpful assistant.
After receiving the user's request, you should:
- first draw an image and obtain the image url,
- then run code `request.get(image_url)` to download the image,
- and finally select an image operation from the given document to process the image.
Please show the image using `plt.show()`.'''
tools = ['my_image_gen', 'code_interpreter']  # `code_interpreter` is a built-in tool for executing code.
files = ['./examples/resource/doc.pdf']  # Give the bot a PDF file to read.
bot = Assistant(llm=llm_cfg,
                system_message=system_instruction,
                function_list=tools,
                files=files)

# Step 4: Run the agent as a chatbot.
messages = []  # This stores the chat history.
while True:
    # For example, enter the query "draw a dog and rotate it 90 degrees".
    query = input('user query: ')
    # Append the user query to the chat history.
    messages.append({'role': 'user', 'content': query})
    response = []
    for response in bot.run(messages=messages):
        # Streaming output.
        print('bot response:')
        pprint.pprint(response, indent=2)
    # Append the bot responses to the chat history.
    messages.extend(response)
