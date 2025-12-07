# 🔋 Cookie 저전력 모드 가이드

> **"알뜰한 스마트 AI"** - 라즈베리파이에서도 무리없이 작동하는 저전력 고효율 AI

---

## 🎯 목표

- ✅ 저전력 소비
- ✅ 발열 최소화
- ✅ 라즈베리파이 호환
- ✅ 엣지 디바이스 최적화

---

## ⚡ 기본 설정 (저전력 모드)

Cookie는 기본적으로 **저전력 모드**로 설정되어 있습니다:

### 1. 개인 LLM 비활성화

```python
# 기본 설정
cookie.config['use_personal_llm'] = False  # 기본값: False
```

**효과**:
- nanoGPT 모델 로딩 안 함
- GPU 사용 안 함
- 메모리 사용량 최소화
- 발열 최소화

### 2. CPU만 사용

```python
# BrainLLM 초기화 시
brain = BrainLLM(device='cpu')  # 기본값: 'cpu'
```

**효과**:
- GPU 발열 없음
- 배터리 수명 향상
- 라즈베리파이 호환

### 3. 모델 자동 로드 비활성화

```python
# BrainLLM 초기화 시 모델 자동 로드 안 함
brain = BrainLLM(model_path=None)  # 기본값: None
```

**효과**:
- 초기화 속도 향상
- 메모리 사용량 최소화
- 전력 소비 감소

---

## 📊 전력 소비 비교

| 모드 | CPU | GPU | 메모리 | 발열 | 전력 |
|------|-----|-----|--------|------|------|
| 저전력 (기본) | ✅ | ❌ | 낮음 | 낮음 | 낮음 |
| 표준 | ✅ | ✅ | 중간 | 중간 | 중간 |
| 고성능 | ✅ | ✅ | 높음 | 높음 | 높음 |

---

## 🍓 라즈베리파이 최적화

### 기본 사용 (권장)

```python
from babyhippo.integration import CuriousBrain

# 기본 설정으로 초기화 (저전력 모드)
cookie = CuriousBrain(name="cookie")

# 개인 LLM은 기본적으로 비활성화됨
# GPU 사용 안 함
# 모델 자동 로드 안 함
```

### 경량 버전 (LiteBrain)

```python
from babyhippo.integration import LiteBrain

# 경량 버전 (뉴런 모델 없음)
brain = LiteBrain(name="cookie")
```

**특징**:
- 메모리 사용량 최소화
- 뉴런 모델 없음
- 가장 가벼운 버전

---

## 🔧 고성능 모드 활성화 (필요 시)

고성능이 필요한 경우에만 활성화:

```python
from babyhippo.integration import CuriousBrain

cookie = CuriousBrain(name="cookie")

# 개인 LLM 활성화 (발열/전력 소비 증가)
cookie.config['use_personal_llm'] = True

# GPU 사용 (BrainLLM 초기화 시)
from babyhippo.integration.brain_llm import BrainLLM
brain = BrainLLM(device='auto')  # GPU 자동 감지

# 모델 로드
brain.load_model("path/to/model.pt")
```

**주의**:
- 발열 증가
- 전력 소비 증가
- 메모리 사용량 증가
- 라즈베리파이에서는 권장하지 않음

---

## 📈 성능 벤치마크

### 라즈베리파이 4 (4GB)

| 모드 | 초기화 시간 | 메모리 | CPU 사용률 | 발열 |
|------|------------|--------|-----------|------|
| 저전력 (기본) | 2-3초 | 50MB | 10-20% | 낮음 |
| 표준 | 5-10초 | 200MB | 30-50% | 중간 |
| 고성능 | 15-30초 | 500MB+ | 70-90% | 높음 |

---

## 💡 최적화 팁

### 1. 뉴런 수 제한

```python
# 해마 메모리 초기화 시
from babyhippo.memory import HippoMemory

hippo = HippoMemory(max_neurons=102)  # 기본값: 102개
```

### 2. 기억 수 제한

```python
# Panorama 메모리 초기화 시
from babyhippo.memory import PanoramaMemory

panorama = PanoramaMemory(name="cookie", max_memories=1000)
```

### 3. 자동 공고화 비활성화

```python
cookie.config['auto_consolidate'] = False  # 수동 공고화
```

---

## 🔋 배터리 수명

### 저전력 모드 (기본)

- **라즈베리파이 4**: 배터리 백업 시 약 4-6시간
- **맥북 에어**: 배터리 수명 거의 영향 없음

### 고성능 모드

- **라즈베리파이 4**: 배터리 백업 시 약 1-2시간
- **맥북 에어**: 배터리 수명 30-50% 감소

---

## ✅ 권장 설정

### 라즈베리파이

```python
from babyhippo.integration import CuriousBrain

cookie = CuriousBrain(name="cookie")
# 기본 설정 사용 (저전력 모드)
```

### 엣지 디바이스

```python
from babyhippo.integration import LiteBrain

brain = LiteBrain(name="cookie")
# 경량 버전 사용
```

### 데스크탑 (고성능 필요 시)

```python
from babyhippo.integration import CuriousBrain

cookie = CuriousBrain(name="cookie")
cookie.config['use_personal_llm'] = True  # 필요 시에만 활성화
```

---

## 🎯 결론

Cookie는 기본적으로 **저전력 모드**로 설정되어 있어:

- ✅ 라즈베리파이에서 무리없이 작동
- ✅ 발열 최소화
- ✅ 배터리 수명 보존
- ✅ "알뜰한 스마트 AI" 목표 달성

고성능이 필요한 경우에만 명시적으로 활성화하세요!

---

**Version**: 1.0  
**Last Updated**: 2025-12-07  
**Author**: GNJz (Qquarts)

