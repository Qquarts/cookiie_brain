# 🍪 Cookie 대화형 챗봇 작동 원리

## 📋 개요

Cookie는 **"뇌처럼"** 학습하고 대화하는 AI입니다. GPT/LLaMA 같은 대규모 언어 모델과는 다른 방식으로 작동합니다.

---

## 🔄 전체 흐름도

```
사용자 입력
    ↓
[1] 입력 분류 (질문 vs 학습 명령)
    ├─ 질문? → [2] 답변 경로
    └─ 학습 명령? → [3] 학습 경로
    ↓
[2] 답변 경로 (think 메서드)
    ├─ [2-1] 간단한 질문 → 즉시 응답 (QUICK_RESPONSES)
    ├─ [2-2] 해마(기억) 검색 → 기억에서 답변
    ├─ [2-3] 개인 LLM 시도 → 짧은 응답 생성
    ├─ [2-4] 도서관(외부 LLM) 방문 → 답변 받기
    └─ [2-5] 기억에서라도 찾기 → fallback
    ↓
[3] 학습 경로 (learn 메서드)
    ├─ 질문 필터링 (질문이면 차단)
    └─ 해마에 저장
    ↓
응답 출력
```

---

## 🧠 1단계: 입력 분류 (Input Classification)

### 질문 감지 (`_is_question_strict`)

```python
def _is_question_strict(text: str) -> bool:
    """
    질문인지 검사
    - 물음표(?)
    - 한국어 의문형 종결어미 (뭐야, 어때, 기억나 등)
    - 질문 패턴 (뭐, 무엇, 어떻게 등)
    """
```

**예시**:
- "이름이 뭐야?" → 질문 (답변 경로)
- "나는 GNJz라고 해" → 학습 명령 (학습 경로)

### 학습 명령 감지

```python
# 학습 명령 패턴
learning_patterns = ['라고 해', '라고 해요', '라고 합니다']
name_intro_patterns = ['내 이름은', '나는', '저는']
```

**예시**:
- "학습: 사과는 빨간색" → 학습 명령
- "나는 GNJz라고 해" → 학습 명령

---

## 💬 2단계: 답변 경로 (Answer Path)

### `think(question: str) -> str` 메서드

#### 2-1. 간단한 질문 → 즉시 응답 (비용 절약)

```python
QUICK_RESPONSES = {
    '안녕': '안녕하세요! 😊',
    '안녕하세요': '안녕하세요! 😊',
    '고마워': '천만에요! 😊',
    # ...
}
```

**예시**: "안녕" → "안녕하세요! 😊"

#### 2-2. 해마(기억) 검색

```python
# 키워드 추출
question_keywords = self._extract_keywords(question)

# 해마에서 검색
memories = self.brain.recall(keyword, top_n=5)

# 출력 포맷팅
answer = self._format_output(memory_content, question)
```

**예시**:
- 질문: "사과는 무슨 색이야?"
- 기억: "사과는 빨간색"
- 출력: "사과는 빨간색입니다."

#### 2-3. 개인 LLM 시도

```python
# nanoGPT 기반 개인 LLM
personal_answer = self._generate_clean_response(question)
```

**예시**: 짧은 응답 생성

#### 2-4. 도서관(외부 LLM) 방문

```python
# OpenAI, Anthropic 등
library_answer, success = self.library.ask(question)

# 배운 것 저장
if success:
    self.brain.learn(library_answer, importance=0.8)
```

**예시**:
- 질문: "파이썬이 뭐야?"
- 도서관 답변: "파이썬은 프로그래밍 언어입니다."
- 저장: 해마에 저장됨

#### 2-5. 기억에서라도 찾기 (Fallback)

```python
# 낮은 점수라도 기억이 있으면 시도
if memories:
    potential_answer = memories[0].get('content')
    # 포맷팅 후 반환
```

---

## 📝 3단계: 학습 경로 (Learning Path)

### `learn(content: str, importance: float) -> None`

```python
def learn(self, content: str, importance: float = 0.7):
    # 1. 질문 필터링 (질문이면 차단)
    if self._is_question_strict(content):
        return  # 거울 효과 방지
    
    # 2. 해마에 저장
    self.brain.learn(content, importance=importance)
```

**예시**:
- "나는 GNJz라고 해" → 해마에 저장
- "이름이 뭐야?" → 저장 차단 (질문)

---

## 🔧 핵심 메커니즘

### 1. 질문 필터링 (Anti-Contamination Filter)

```python
def _is_question_strict(text: str) -> bool:
    # 물음표(?)
    if text.endswith('?'):
        return True
    
    # 한국어 의문형 종결어미
    # 띄어쓰기 무시 검사
    cleaned_text = text.replace(" ", "")
    if re.search(r'뭐야$|어때$|기억나$', cleaned_text):
        return True
    
    return False
```

**목적**: 질문이 기억 저장소에 저장되는 것을 차단

### 2. 출력 포맷팅 (Output Formatting)

```python
def _format_output(raw_content: str, question: str = "") -> str:
    # 1. 질문 필터링
    if self._is_question_strict(raw_content):
        return "기억이 명확하지 않아요."
    
    # 2. 파편 필터링
    if len(raw_content) < 3:
        return "기억이 불완전합니다."
    
    # 3. 학습 명령 형태 변환
    if '라고 해' in raw_content:
        # "나는GNJz 라고 해" → "당신의 이름은 GNJz입니다."
        name = extract_name(raw_content)
        return f"당신의 이름은 {name}입니다."
    
    # 4. 완전한 문장으로 변환
    return f"{raw_content}입니다."
```

**목적**: 날것 기억을 완전한 서술형 문장으로 변환

### 3. 맥락 관리 (Context Management)

```python
# 대화 맥락 저장
self.conversation_context.append({
    'question': question,
    'answer': answer,
    'source': 'memory'  # 'memory', 'library', 'learning'
})

# 이전 대화 참조
def _enhance_with_context(question: str) -> str:
    # "그거" → 이전 질문의 주제로 대체
    if '그거' in question:
        return previous_question_topic
```

**목적**: 연속 대화 지원 ("그거 뭐야?" 같은 맥락 질문)

---

## 📊 실제 대화 예시

```
👤 사용자: 안녕
🍪 Cookie: 안녕하세요! 😊
   → QUICK_RESPONSES에서 즉시 응답

👤 사용자: 나는 GNJz라고 해
🍪 Cookie: 알겠어요! GNJz이라고 기억할게요! 😊
   → 학습 경로: 해마에 저장

👤 사용자: 나는?
🍪 Cookie: 당신의 이름은 GNJz입니다.
   → 답변 경로: 해마에서 검색 → 포맷팅

👤 사용자: 사과는 무슨 색이야?
🍪 Cookie: 모르겠어요.
   → 답변 경로: 기억 없음 → 도서관 방문
   → 도서관: "사과는 빨간색입니다."
   → 저장: 해마에 저장

👤 사용자: 사과는 무슨 색이야?
🍪 Cookie: 사과는 빨간색입니다.
   → 답변 경로: 해마에서 검색 → 답변
```

---

## 🎯 핵심 원리

### 1. **우선순위 기반 검색**
```
해마(기억) > 개인 LLM > 도서관(외부 LLM)
```

### 2. **학습 루프**
```
질문 → 답변 → 저장 → 성장
```

### 3. **필터링 시스템**
```
질문 필터 → 학습 차단
출력 포맷팅 → 완전한 문장 보장
```

### 4. **맥락 관리**
```
대화 기록 → 연속 질문 처리
```

---

## 🔍 코드 흐름

### `think()` 메서드 실행 순서

```python
def think(self, question: str) -> str:
    # 0. 질문/학습 분류
    if is_question:
        # 답변 경로
        pass
    elif is_learning_command:
        # 학습 경로
        self.learn(question)
        return "학습 완료!"
    
    # 1. 간단한 질문 → 즉시 응답
    if question in QUICK_RESPONSES:
        return QUICK_RESPONSES[question]
    
    # 2. 해마 검색
    memories = self.brain.recall(question_keywords)
    if memories:
        answer = self._format_output(memories[0], question)
        return answer
    
    # 3. 개인 LLM 시도
    personal_answer = self._generate_clean_response(question)
    if personal_answer:
        return personal_answer
    
    # 4. 도서관 방문
    library_answer, success = self.library.ask(question)
    if success:
        # 배운 것 저장
        self.brain.learn(library_answer, importance=0.8)
        return library_answer
    
    # 5. Fallback
    return "모르겠어요."
```

---

## 💡 핵심 차이점

### GPT/LLaMA vs Cookie

| 항목 | GPT/LLaMA | Cookie |
|------|-----------|--------|
| 학습 방식 | 사전 학습 (Pre-training) | 실시간 학습 (Online Learning) |
| 기억 | 컨텍스트 윈도우 | 해마 기억 시스템 |
| 응답 | 생성 모델 | 기억 검색 + 생성 |
| 성장 | 고정 | 점진적 성장 (진화 단계) |

---

**Version**: 1.0  
**Last Updated**: 2025-12-07  
**Author**: GNJz (Qquarts)

