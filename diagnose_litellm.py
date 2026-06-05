#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""LiteLLM 问题诊断脚本"""

import sys
import os
from pathlib import Path

# 添加项目到路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

# 第一步：启用 LiteLLM 完整调试
import litellm
litellm._turn_on_debug()

# 第二步：设置日志捕捉
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('litellm_diagnosis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# 第三步：加载配置
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*70)
print("🔍 LiteLLM 诊断开始")
print("="*70)

# 检查环境变量
print("\n📋 环境变量检查：")
required_vars = [
    'STOCK_LIST',
    'LITELLM_MODEL',
    'GEMINI_API_KEY',
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
]

for var in required_vars:
    value = os.getenv(var, '未设置')
    if value != '未设置':
        # 只显示前缀，隐藏完整密钥
        value = value[:15] + '...' if len(value) > 15 else value
    print(f"  {var}: {value}")

# 检查配置加载
print("\n⚙️ 配置加载测试：")
try:
    from src.config import get_config
    config = get_config()
    print(f"  ✓ 配置加载成功")
    print(f"    - 主模型: {config.litellm_model}")
    print(f"    - 股票列表: {config.stock_list}")
except Exception as e:
    print(f"  ✗ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 检查 LiteLLM 模型支持
print("\n🤖 LiteLLM 模型检查：")
if config.litellm_model:
    try:
        print(f"  测试模型: {config.litellm_model}")
        
        # 提取 provider
        if '/' in config.litellm_model:
            provider = config.litellm_model.split('/')[0]
            print(f"  Provider: {provider}")
        
        # 检查模型是否在 litellm 支持列表中
        supported_models = litellm.models_list if hasattr(litellm, 'models_list') else []
        print(f"  LiteLLM 支持的模型数: {len(supported_models)}")
        
    except Exception as e:
        print(f"  ✗ 模型检查失败: {e}")

# 关键：尝试调用 LiteLLM API（这会触发真实的错误信息）
print("\n🔗 API 连接测试（这会显示真实错误）：")
print("-" * 70)

try:
    response = litellm.completion(
        model=config.litellm_model,
        messages=[
            {"role": "user", "content": "Hello, this is a test message."}
        ],
        max_tokens=10,
        temperature=0.7,
    )
    print(f"  ✓ API 调用成功!")
    print(f"  响应: {response}")
    
except litellm.AuthenticationError as e:
    print(f"  ✗ 认证错误 (Authentication Error):")
    print(f"    {e}")
    print(f"\n  💡 解决方案:")
    print(f"    1. 检查 API Key 是否正确")
    print(f"    2. 确保 API Key 没有过期")
    print(f"    3. 确保 API Key 有足够的权限")
    
except litellm.RateLimitError as e:
    print(f"  ✗ 速率限制错误 (Rate Limit Error):")
    print(f"    {e}")
    print(f"\n  💡 解决方案:")
    print(f"    1. 等待 60 秒后重试")
    print(f"    2. 配置备用模型: LITELLM_FALLBACK_MODELS")
    print(f"    3. 减少并发数: MAX_WORKERS=1")
    
except litellm.APIError as e:
    print(f"  ✗ API 错误:")
    print(f"    {e}")
    print(f"\n  💡 解决方案:")
    print(f"    1. 检查网络连接")
    print(f"    2. 检查 API 服务状态")
    print(f"    3. 查看详细日志: cat litellm_diagnosis.log")
    
except Exception as e:
    print(f"  ✗ 未知错误:")
    print(f"    类型: {type(e).__name__}")
    print(f"    信息: {e}")
    import traceback
    print("\n  详细堆栈:")
    traceback.print_exc()

print("\n" + "="*70)
print("📊 诊断完成")
print("📄 详细日志已保存到: litellm_diagnosis.log")
print("="*70 + "\n")
