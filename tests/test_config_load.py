# tests/test_config_load.py

import pytest
from cabsaia.config import CABSAIAConfig


def test_config_default_values():
    """验证默认配置是否包含关键字段且具有合理值"""
    config = CABSAIAConfig()

    # 基本字段存在性和类型检查
    assert isinstance(config.DEBUG, bool)
    assert config.DEFAULT_LLM in ("gpt-3.5-turbo", "gpt-4", "mistral")
    assert isinstance(config.EMOTIONAL_GRANULARITY, int)
    assert config.MAX_TOKENS > 100

    # 检查路径字段是否被正确设置
    assert config.MODEL_DIR.exists() or config.MODEL_DIR.name == "models"
    assert config.DATA_DIR.exists() or config.DATA_DIR.name == "data"


def test_config_dynamic_update():
    """验证 update 方法能成功修改配置项"""
    config = CABSAIAConfig()
    old_temp = config.LLM_TEMPERATURE
    config.update(LLM_TEMPERATURE=0.42)

    assert config.LLM_TEMPERATURE == 0.42
    assert config.LLM_TEMPERATURE != old_temp
