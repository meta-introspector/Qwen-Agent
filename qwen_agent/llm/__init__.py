import copy
from typing import Union

from .azure import TextChatAtAzure
from .base import LLM_REGISTRY, BaseChatModel, ModelServiceError
from .oai import TextChatAtOAI
from .openvino import OpenVINO
#from .qwen_dashscope import QwenChatAtDS
#from .qwenvl_dashscope import QwenVLChatAtDS
from .qwenvl_oai import QwenVLChatAtOAI


def get_chat_model(cfg: Union[dict, str] = {
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
) -> BaseChatModel:
    print("GET MODEL", cfg)
    """The interface of instantiating LLM objects.

    Args:
        cfg: The LLM configuration, one example is:
          cfg = {
              # Use the model service provided by DashScope:
#              'model': 'qwen-max',
#              'model_server': 'dashscope',

              # Use your own model service compatible with OpenAI API:
    model:'qwen2.5-coder',
              # 'model': 'Qwen',
              'model_server': 'http://localhost:11434/v1/',

              # (Optional) LLM hyper-parameters:
              'generate_cfg': {
                  'top_p': 0.8,
                  'max_input_tokens': 6500,
                  'max_retries': 10,
              }
          }

    Returns:
        LLM object.
    """
    if isinstance(cfg, str):
        cfg = {'model': cfg}

    if 'model_type' in cfg:
        model_type = cfg['model_type']
        if model_type in LLM_REGISTRY:
#            if model_type in ('oai', 'qwenvl_oai'):
#                if cfg.get('model_server', '').strip() == 'dashscope':
#                    cfg = copy.deepcopy(cfg)
#                    cfg['model_server'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
            return LLM_REGISTRY[model_type](cfg)
        else:
            raise ValueError(f'Please set model_type from {str(LLM_REGISTRY.keys())}')

    # Deduce model_type from model and model_server if model_type is not provided:

    if 'azure_endpoint' in cfg:
        model_type = 'azure'
        return LLM_REGISTRY[model_type](cfg)

    if 'model_server' in cfg:
        if cfg['model_server'].strip().startswith('http'):
            model_type = 'oai'
            return LLM_REGISTRY[model_type](cfg)

    model = cfg.get('model', '')

    if 'qwen' in model:
        model_type = cfg.get('model_type', 'oai')
        return LLM_REGISTRY[model_type](cfg)

    raise ValueError(f'Invalid model cfg: {cfg}')


__all__ = [
    'BaseChatModel',
    'QwenChatAtDS',
    'TextChatAtOAI',
    'TextChatAtAzure',
    'QwenVLChatAtDS',
    'QwenVLChatAtOAI',
    'OpenVINO',
    'get_chat_model',
    'ModelServiceError',
]
