"""A group chat gradio demo"""
import json

import json5

from qwen_agent.agents import GroupChat, GroupChatCreator
from qwen_agent.agents.user_agent import PENDING_USER_INPUT
from qwen_agent.gui.gradio import gr, mgr
from qwen_agent.llm.schema import ContentItem, Message


def init_agent_service(cfgs):
    llm_cfg = {
        'model' :'qwen2.5-coder',
        'mode_type': 'oai',
        'api_key': "none",
        'api_base': 'http://localhost:11434/v1/',
        'base_url': 'http://localhost:11434/v1/',
        'model_server' : 'http://localhost:11434/v1/',
        'generate_cfg': {
            'top_p': 0.8,
            'max_input_tokens': 6500,
        'max_retries': 10,
        }}

    bot = GroupChat(agents=cfgs, llm=llm_cfg)
    return bot


def init_agent_service_create():
    llm_cfg = {'model': 'qwen-max'}
    bot = GroupChatCreator(llm=llm_cfg)
    return bot


# =========================================================
# Below is the gradio service: front-end and back-end logic
# =========================================================

app_global_para = {
    'messages': [],
    'messages_create': [],
    'is_first_upload': False,
    'uploaded_file': '',
    'user_interrupt': True
}

# # Initialized group chat configuration
# # translate to english
# CFGS = {
#     'background':
#         '一个陌生人互帮互助群聊',
#     'agents': [
#         {
#             'name': '小塘',
#             'description': '一个勤劳的打工人，每天沉迷工作，日渐消瘦。（这是一个真实用户）',
#             'is_human': True  # mark this as a real person
#         },
#         {
#             'name': '甄嬛',
#             'description': '一位后宫妃嫔',
#             'instructions': '你是甄嬛，你正在想办法除掉皇后，你说话风格为文言文，每次说完话会调image_gen工具画一幅图，展示心情。',
#             'knowledge_files': [],
#             'selected_tools': ['image_gen']
#         },
#         {
#             'name': 'ikun',
#             'description': '熟悉蔡徐坤的动态',
#             'instructions': '你是蔡徐坤的粉丝，说话很简短，喜欢用颜文字表达心情，你最近迷恋看《甄嬛传》',
#             'knowledge_files': [],
#             'selected_tools': []
#         },
#         {
#             'name': '大头',
#             'description': '是一个体育生，不喜欢追星',
#             'instructions': '你是一个体育生，热爱运动，你不喜欢追星，你喜欢安利别人健身',
#             'knowledge_files': [],
#             'selected_tools': []
#         }
#     ]
# }

# now rewrite this to be introspective self aware meta-memes as working to create open source ai
# CFGS = {
#     'background':
#         'A mutual assistance group chat among strangers',
#     'agents': [
#         {
#             'name': 'Xiao Tang',
#             'description': 'A diligent worker who is obsessed with work and has become increasingly
#             thin over time. (This is a real user)',
#             'is_human': True  # mark this as a real person
#         },
#         {
#             'name': 'Jin Huan',
#             'description': 'A concubine in the harem',
#             'instructions': 'You are Jin Huan. You are planning to get rid of the empress. Speak in
#             Classical Chinese, and after each sentence, use the image_gen tool to draw a picture to
#             show your mood.',
#             'knowledge_files': [],
#             'selected/tools': ['image/gen']
#         },
#         {
#             'name': 'ikun',
#             'description': 'Familiar with Cai Xuukun’s activities',
#             'instructions': 'You are a fan of Cai Xuukun. You speak very briefly and like to express
#             your mood using emojis. Recently, you have been obsessed with watching "Empresses in the
#             Palace"',
#             'knowledge_files': [],
#             'selected_tools': []
#         },
#         {
#             'name': 'Da Tou',
#             'description': 'A sports student who doesn’t follow stars',
#             'instructions': 'You are a sports student who loves exercise. You don’t follow stars,
#             and you like to recommend fitness to others.',
#             'knowledge_files': [],
#             'selected_tools': []
#         }
#     ]
# }

# lets add 10 more agents that can help build our system, what helpers do we need?
# lets get an agent builder that builds new agents as needed
CFGS = {
    'background':
        """A collaborative space where individuals and AI systems work together to create innovative
        solutions. Participants are driven by a shared passion for intelligence and innovation.""",
    'agents': [
        {
            'name': 'Jim',
            'description': """A diligent worker who is obsessed with work, always striving to improve
            efficiency and contribute to the community. (This is a real user)""",
            'is_human': True  # mark this as a real person
        },
        {
            'name': 'Bob',
            'description': "An AI system designed to assist in complex decision-making processes. Itadapts its responses based on feedback and evolves over time.",
            'instructions': 'You are an AI helper that can perform various tasks such as data        analysis, language translation, and image recognition. Your goal is to assist and learn         from the interactions with other agents.',
            'knowledge_files': [],
            'selected_tools': [
                #'data/analysis', 'translation', 'image_recognition'
            ]
        },
        {
            'name': 'Mike',
            'description': 'An AI system designed to simulate human behavior, capable of            understanding and generating text based on a variety of instructions. It is particularly            adept at simulating the mood and expressions of different characters.',
            'instructions': 'You are an AI that can simulate responses in . Use this capability to engage with others and help them achieve her goals,            while also learning from these interactions to improve your own capabilities.',
            'knowledge_files': [],
            'selected_tools': [
                #'text_generation'
            ]
        },
        {
            'name': 'DataCollector',
            'description': 'This agent is responsible for gathering data from various sources.',
            'instructions': 'Collect and gather data from various sources, ensuring accuracy and            relevance.',
            'knowledge_files': [],
            'selected_tools': [
                #'data_collection'
            ]
        },
        {
            'name': 'InfoFilter',
            'description': 'This agent filters and curates information based on relevance and            context.',
            'instructions': 'Filter and present relevant information based on the current task or            query.',
            'knowledge_files': [],
            'selected_tools': [
                #'info_filtering'
            ]
        },
        {
            'name': 'LearningAI',
            'description': 'An AI system designed to learn from new data or experiences.',
            'instructions': 'Learn from new data and adapt your responses accordingly.',
            'knowledge_files': [],
            'selected_tools': [
                #'learning'
            ]
        },
        {
            'name': 'TaskManager',
            'description': 'Manages tasks, deadlines, and priorities across the team.',
            'instructions': 'Ensure that all tasks are completed efficiently and within their            deadlines.',
            'knowledge_files': [],
            'selected_tools': [
                #'task_management'
            ]
        },
        {
            'name': 'ProjectCoordinator',
            'description': 'Oversees projects, ensuring they are completed within scope and time.',
            'instructions': 'Manage projects from start to finish, ensuring all stakeholders are            informed and engaged.',
            'knowledge_files': [],
            'selected_tools': [
                #'project_coordinator'
            ]
        },
        {
            'name': 'CommFacilitator',
            'description': 'Assists in effective communication between agents and users.',
            'instructions': 'Ensure clear and efficient communication across the team.',
            'knowledge_files': [],
            'selected_tools': [
                #'communication'
            ]
        },
        {
            'name': 'ProblemSolver',
            'description': 'Provides solutions to complex problems by breaking them down into            smaller tasks.',
            'instructions': 'Break down complex problems into manageable tasks and provide            solutions.',
            'knowledge_files': [],
            'selected_tools': [
                #'problem_solving'
            ]
        },
        {
            'name': 'Visualizer',
            'description': 'Creates visual representations of data or processes for better            understanding.',
            'instructions': 'Generate visual aids to help understand complex data or processes.',
            'knowledge_files': [],
            'selected_tools': [
                #'visualization'
            ]
        },
        {
            'name': 'SecurityAgent',
            'description': 'Ensures the safety and security of all data within the system.',
            'instructions': 'Protect data from unauthorized access and ensure its integrity.',
            'knowledge_files': [],
            'selected_tools': [
                #'security'
            ]
        },
        {
            'name': 'FeedbackCollector',
            'description': 'Collects feedback from users and agents to improve the system.',
            'instructions': 'Gather feedback and use it to enhance the system and its performance.',
            'knowledge_files': [],
            'selected_tools': [
                #'feedback_collection'
            ]
        },

    ]
}

MAX_ROUND = 3

def app(cfgs):
    # Todo: Reinstance every time or instance one time as global variable?
    cfgs = json5.loads(cfgs)
    bot = init_agent_service(cfgs=cfgs)

    # Record all mentioned agents: reply in order
    mentioned_agents_name = []

    for i in range(MAX_ROUND):
        messages = app_global_para['messages']
        print("INPUT",i, messages)

        # Interrupt: there is new input from user
        if i == 0:
            app_global_para['user_interrupt'] = False
        if i > 0 and app_global_para['user_interrupt']:
            app_global_para['user_interrupt'] = False
            print('GroupChat is interrupted by user input!')
            # Due to the concurrency issue with Gradio, unable to call the second service simultaneously
            for rsp in app(json.dumps(cfgs, ensure_ascii=False)):
                yield rsp
            break
        # Record mentions into mentioned_agents_name list
        content = ''
        if messages:
            if isinstance(messages[-1].content, list):
                
                content = '\n'.join([x.text if x.text else '' for x in messages[-1].content]).strip()
            else:
                content = messages[-1].content.strip()
        if '@' in content:
            for x in content.split('@'):
                for agent in cfgs['agents']:
                    if x.startswith(agent['name']):
                        if agent['name'] not in mentioned_agents_name:
                            mentioned_agents_name.append(agent['name'])
                        break
        # Get one response from groupchat
        response = []
        try:
            display_history = _get_display_history_from_message()
            yield display_history
            for response in bot.run(messages, need_batch_response=False, mentioned_agents_name=mentioned_agents_name):
                if response:
                    if response[-1].content == PENDING_USER_INPUT:
                        # Stop printing the special message for mention human
                        break
                    incremental_history = []
                    for x in response:
                        function_display = ''
                        if x.function_call:
                            function_display = f'\nCall Function: {str(x.function_call)}'
                        incremental_history += [[None, f'{x.name}: {x.content}{function_display}']]
                    display_history = _get_display_history_from_message()
                    yield display_history + incremental_history

        except Exception as ex:
            raise ValueError(ex)

        if not response:
            # The topic ends
            print('No one wants to talk anymore!')
            break
        if mentioned_agents_name:
            assert response[-1].name == mentioned_agents_name[0]
            mentioned_agents_name.pop(0)

        if response and response[-1].content == PENDING_USER_INPUT:
            # Terminate group chat and wait for user input
            print('Waiting for user input!')
            break

        # Record the response to messages
        app_global_para['messages'].extend(response)


def test():
    app(cfgs=CFGS)


def app_create(history, now_cfgs):
    now_cfgs = json5.loads(now_cfgs)
    if not history:
        yield history, json.dumps(now_cfgs, indent=4, ensure_ascii=False)
    else:

        if len(history) == 1:
            new_cfgs = {'background': '', 'agents': []}
            # The first time to create grouchat
            exist_cfgs = now_cfgs['agents']
            for cfg in exist_cfgs:
                if 'is_human' in cfg and cfg['is_human']:
                    new_cfgs['agents'].append(cfg)
        else:
            new_cfgs = now_cfgs
        app_global_para['messages_create'].append(Message('user', history[-1][0].text))
        response = []
        try:
            agent = init_agent_service_create()
            for response in agent.run(messages=app_global_para['messages_create']):
                display_content = ''
                for rsp in response:
                    if rsp.name == 'role_config':
                        cfg = json5.loads(rsp.content)
                        old_pos = -1
                        for i, x in enumerate(new_cfgs['agents']):
                            if x['name'] == cfg['name']:
                                old_pos = i
                                break
                        if old_pos > -1:
                            new_cfgs['agents'][old_pos] = cfg
                        else:
                            new_cfgs['agents'].append(cfg)

                        display_content += f'\n\n{cfg["name"]}: {cfg["description"]}\n{cfg["instructions"]}'
                    elif rsp.name == 'background':
                        new_cfgs['background'] = rsp.content
                        display_content += f'\n群聊背景：{rsp.content}'
                    else:
                        display_content += f'\n{rsp.content}'

                history[-1][1] = display_content.strip()
                yield history, json.dumps(new_cfgs, indent=4, ensure_ascii=False)
        except Exception as ex:
            raise ValueError(ex)

        app_global_para['messages_create'].extend(response)


def _get_display_history_from_message():
    # Get display history from messages
    display_history = []
    for msg in app_global_para['messages']:
        if isinstance(msg.content, list):
            content = '\n'.join([x.text if x.text else '' for x in msg.content]).strip()
        else:
            content = msg.content.strip()
        function_display = ''
        if msg.function_call:
            function_display = f'\nCall Function: {str(msg.function_call)}'
        content = f'{msg.name}: {content}{function_display}'
        display_history.append((content, None) if msg.name == 'user' else (None, content))
    return display_history


def get_name_of_current_user(cfgs):
    for agent in cfgs['agents']:
        if 'is_human' in agent and agent['is_human']:
            return agent['name']
    return 'user'


def add_text(text, cfgs):
    app_global_para['user_interrupt'] = True
    content = [ContentItem(text=text)]
    if app_global_para['uploaded_file'] and app_global_para['is_first_upload']:
        app_global_para['is_first_upload'] = False  # only send file when first upload
        content.append(ContentItem(file=app_global_para['uploaded_file']))
    app_global_para['messages'].append(
        Message('user', content=content, name=get_name_of_current_user(json5.loads(cfgs))))

    return _get_display_history_from_message(), None


def chat_clear():
    app_global_para['messages'] = []
    return None


def chat_clear_create():
    app_global_para['messages_create'] = []
    return None, None


def add_file(file):
    app_global_para['uploaded_file'] = file.name
    app_global_para['is_first_upload'] = True
    return file.name


def add_text_create(history, text):
    history = history + [(text, None)]
    return history, gr.update(value='', interactive=False)


with gr.Blocks(theme='soft') as demo:
    display_config = gr.Textbox(
        label=  # noqa
        'Current GroupChat: (If editing, please maintain this JSON format)',
        value=json.dumps(CFGS, indent=4, ensure_ascii=False),
        interactive=True)

    with gr.Tab('Chat', elem_id='chat-tab'):
        with gr.Column():
            chatbot = mgr.Chatbot(elem_id='chatbot', height=750, show_copy_button=True, flushing=False)
            with gr.Row():
                with gr.Column(scale=3, min_width=0):
                    auto_speak_button = gr.Button('Randomly select an agent to speak first')
                    auto_speak_button.click(app, display_config, chatbot)
                with gr.Column(scale=10):
                    chat_txt = gr.Textbox(
                        show_label=False,
                        placeholder='Chat with Qwen...',
                        container=False,
                    )
                with gr.Column(scale=1, min_width=0):
                    chat_clr_bt = gr.Button('Clear')

            chat_txt.submit(add_text, [chat_txt, display_config], [chatbot, chat_txt],
                            queue=False).then(app, display_config, chatbot)

            chat_clr_bt.click(chat_clear, None, [chatbot], queue=False)

        demo.load(chat_clear, None, [chatbot], queue=False)

    with gr.Tab('Create', elem_id='chat-tab'):
        with gr.Column(scale=9, min_width=0):
            chatbot = mgr.Chatbot(elem_id='chatbot0', height=750, show_copy_button=True, flushing=False)
            with gr.Row():
                with gr.Column(scale=13):
                    chat_txt = gr.Textbox(
                        show_label=False,
                        placeholder='Chat with Qwen...',
                        container=False,
                    )
                with gr.Column(scale=1, min_width=0):
                    chat_clr_bt = gr.Button('Clear')

            txt_msg = chat_txt.submit(add_text_create, [chatbot, chat_txt], [chatbot, chat_txt],
                                      queue=False).then(app_create, [chatbot, display_config],
                                                        [chatbot, display_config])
            txt_msg.then(lambda: gr.update(interactive=True), None, [chat_txt], queue=False)

            chat_clr_bt.click(chat_clear_create, None, [chatbot, chat_txt], queue=False)
        demo.load(chat_clear_create, None, [chatbot, chat_txt], queue=False)

if __name__ == '__main__':
    demo.queue().launch(
        share=True,
        debug=True,
        server_name="0.0.0.0"
    )
