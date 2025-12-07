"""
babyHippo Utilities
Helper functions for memory operations
"""
import numpy as np
import hashlib
import uuid
import re
from typing import List, Optional

def normalize(x, min_val=0.0, max_val=1.0):
    """Normalize value to range [min_val, max_val]"""
    return np.clip(x, min_val, max_val)


def reset_neuron(neuron):
    """Reset neuron to resting state"""
    neuron.reset()


def compute_similarity(cue, word):
    """
    Compute similarity between cue and word
    Simple prefix matching for baby version
    
    Args:
        cue: Search cue (e.g., "ca")
        word: Target word (e.g., "cat")
    
    Returns:
        Similarity score 0.0 ~ 1.0
    """
    if not cue or not word:
        return 0.0
    
    cue = cue.lower()
    word = word.lower()
    
    # Prefix match
    if word.startswith(cue):
        return len(cue) / len(word)
    
    # Substring match
    if cue in word:
        return 0.5 * len(cue) / len(word)
    
    return 0.0


def create_word_id(word):
    """Create unique ID for word"""
    return word.lower().strip()


# ============================================================
# 추가 유틸리티 함수들
# ============================================================

def text_to_vector(text: str, dim: int = 128) -> np.ndarray:
    """
    텍스트를 벡터로 변환 (간단한 해시 기반)
    
    Args:
        text: 입력 텍스트
        dim: 벡터 차원
    
    Returns:
        numpy array
    """
    if not text:
        return np.zeros(dim)
    
    # 해시 기반 시드 생성
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    np.random.seed(seed)
    
    # 랜덤 벡터 생성 및 정규화
    vec = np.random.randn(dim)
    return vec / (np.linalg.norm(vec) + 1e-8)


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    코사인 유사도 계산
    
    Args:
        v1, v2: numpy arrays
    
    Returns:
        -1.0 ~ 1.0
    """
    if v1 is None or v2 is None:
        return 0.0
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 < 1e-8 or norm2 < 1e-8:
        return 0.0
    
    return float(np.dot(v1, v2) / (norm1 * norm2))


def simple_hash(text: str) -> str:
    """
    간단한 해시 생성
    
    Args:
        text: 입력 텍스트
    
    Returns:
        해시 문자열
    """
    return hashlib.md5(text.encode()).hexdigest()[:8]


def generate_uid() -> str:
    """고유 ID 생성"""
    return str(uuid.uuid4())[:8]


def korean_tokenize(text: str) -> List[str]:
    """
    간단한 한국어 토큰화
    
    Args:
        text: 한국어 텍스트
    
    Returns:
        토큰 리스트
    """
    # 공백 기준 분리 + 조사/어미 제거
    tokens = []
    words = text.split()
    
    for word in words:
        # 특수문자 제거
        clean = re.sub(r'[^\w가-힣]', '', word)
        if clean:
            tokens.append(clean)
    
    return tokens


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    키워드 추출 (간단 버전)
    
    Args:
        text: 텍스트
        top_n: 상위 N개
    
    Returns:
        키워드 리스트
    """
    # 불용어
    stopwords = {'은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로', 
                 '와', '과', '하다', '하고', '한다', '했다', '있다', '없다', '되다',
                 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been'}
    
    tokens = korean_tokenize(text)
    
    # 빈도수 계산
    freq = {}
    for token in tokens:
        if token.lower() not in stopwords and len(token) > 1:
            freq[token] = freq.get(token, 0) + 1
    
    # 상위 N개 반환
    sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [token for token, _ in sorted_tokens[:top_n]]


def normalize_korean(text: str) -> str:
    """
    한국어 정규화
    
    Args:
        text: 텍스트
    
    Returns:
        정규화된 텍스트
    """
    # 연속 공백 제거
    text = re.sub(r'\s+', ' ', text)
    # 양쪽 공백 제거
    text = text.strip()
    return text


def smart_truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    단어 경계에서 자르기
    
    Args:
        text: 텍스트
        max_length: 최대 길이
        suffix: 접미사
    
    Returns:
        잘린 텍스트
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    
    # 단어 경계 찾기
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    
    return truncated + suffix
