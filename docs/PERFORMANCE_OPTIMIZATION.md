# ⚡ Cookiie 성능 최적화 가이드

## 🔥 발열 문제 해결

### 원인 분석

맥북 에어가 뜨거워지는 주요 원인:

1. **nanoGPT 모델 로딩**
   - `BrainLLM` 초기화 시 모델 파일이 있으면 자동 로딩
   - Apple Silicon GPU (MPS) 사용 시 발열 발생

2. **해마 메모리 초기화**
   - `HippoMemory()` 초기화 시 뉴런 네트워크 생성
   - 기본 102개 뉴런 제한이지만 초기화는 무거울 수 있음

3. **진화 시스템 초기화**
   - `create_evolution_system()` 호출
   - 블록체인 관련 초기화 (비활성화 가능)

---

## ✅ 해결 방법

### 1. LiteBrain 사용 (경량 버전)

```python
from babyhippo.integration import LiteBrain

# 경량 버전 (뉴런 모델 없음, 메모리 최소화)
brain = LiteBrain(name="cookiie")
```

**장점**:
- 메모리 사용량 최소화
- 발열 최소화
- 빠른 초기화

**단점**:
- 뉴런 모델 없음
- 생물학적 리얼리티 낮음

---

### 2. 개인 LLM 비활성화

```python
from babyhippo.integration import CuriousBrain

cookiie = CuriousBrain(name="cookiie")
cookiie.config['use_personal_llm'] = False  # 개인 LLM 비활성화
```

**효과**:
- nanoGPT 모델 로딩 안 함
- GPU 사용 안 함
- 발열 감소

---

### 3. 모델 경로 제거

```python
from babyhippo.integration import CuriousBrain

# 모델 경로를 None으로 설정
cookiie = CuriousBrain(
    name="cookiie",
    personal_model_path=None  # 명시적으로 None
)
```

**효과**:
- 모델 로딩 시도 안 함
- 초기화 속도 향상

---

### 4. CPU만 사용

```python
from babyhippo.integration.brain_llm import BrainLLM

# CPU만 사용 (GPU 비활성화)
brain = BrainLLM(device='cpu')
```

**효과**:
- GPU 발열 없음
- 배터리 수명 향상

---

## 📊 성능 비교

| 방법 | 메모리 | 발열 | 초기화 속도 | 기능 |
|------|--------|------|------------|------|
| 기본 (CuriousBrain) | 높음 | 높음 | 느림 | 완전 |
| LiteBrain | 낮음 | 낮음 | 빠름 | 기본 |
| LLM 비활성화 | 중간 | 중간 | 중간 | 완전 (LLM 제외) |
| CPU만 사용 | 중간 | 낮음 | 중간 | 완전 |

---

## 🎯 권장 설정

### 맥북 에어 (발열 우려)

```python
from babyhippo.integration import CuriousBrain

cookiie = CuriousBrain(name="cookiie")
cookiie.config['use_personal_llm'] = False  # 개인 LLM 비활성화
```

### 데스크탑 (성능 우선)

```python
from babyhippo.integration import CuriousBrain

cookiie = CuriousBrain(name="cookiie")
# 기본 설정 사용 (모든 기능 활성화)
```

### 엣지 디바이스 (라즈베리파이)

```python
from babyhippo.integration import LiteBrain

brain = LiteBrain(name="cookiie")
# 경량 버전 사용
```

---

## 🔍 모니터링

### 실행 중인 프로세스 확인

```bash
ps aux | grep python
```

### 프로세스 종료

```bash
# 특정 프로세스 종료
killall python3

# 또는 Ctrl+C (터미널에서)
```

---

## 💡 추가 팁

1. **초기화 후 발열 감소**
   - 초기화가 완료되면 발열이 감소합니다
   - 잠시 기다리면 정상 작동합니다

2. **배터리 모드**
   - 배터리 모드에서는 자동으로 성능이 제한됩니다
   - 발열이 자연스럽게 감소합니다

3. **환경 온도**
   - 시원한 환경에서 사용하면 발열이 덜합니다
   - 통풍이 잘 되는 곳에서 사용하세요

---

**Version**: 1.0  
**Last Updated**: 2025-12-07  
**Author**: GNJz (Qquarts)

