"""
Utils: 유틸리티 모듈
=====================

유틸리티 함수들:
- Storage - 저장/로드
- Utils - 텍스트 처리, 해싱 등
- StimulusAccumulator - 자극 축적

Author: GNJz (Qquarts)
"""

from .storage import save_memory, load_memory, list_memory_files, delete_memory

# Storage 클래스 래퍼
class Storage:
    """저장/로드 유틸리티 클래스"""
    save = staticmethod(save_memory)
    load = staticmethod(load_memory)
    list_files = staticmethod(list_memory_files)
    delete = staticmethod(delete_memory)
from .utils import (
    text_to_vector,
    cosine_similarity,
    simple_hash,
    generate_uid,
    korean_tokenize,
    extract_keywords,
    normalize_korean,
    smart_truncate,
)
from .stimulus_accumulator import StimulusAccumulator

__all__ = [
    # Storage
    "Storage",
    # Utils
    "text_to_vector",
    "cosine_similarity",
    "simple_hash",
    "generate_uid",
    "korean_tokenize",
    "extract_keywords",
    "normalize_korean",
    "smart_truncate",
    # StimulusAccumulator
    "StimulusAccumulator",
]

