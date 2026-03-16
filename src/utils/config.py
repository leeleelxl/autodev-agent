"""
配置管理
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """全局配置"""

    # 项目路径
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Model
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")

    # Vector Database
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def ensure_dirs(cls):
        """确保必要的目录存在"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)


# 初始化时创建必要目录
Config.ensure_dirs()
