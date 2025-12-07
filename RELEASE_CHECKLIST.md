# 🚀 GitHub 릴리즈 체크리스트

## 📦 릴리즈 전 확인사항

### ✅ 필수 파일
- [x] README.md (영문)
- [x] README_KO.md (한국어)
- [x] LICENSE
- [x] CHANGELOG.md (최신 버전 업데이트)
- [x] pyproject.toml (버전 확인)
- [x] .gitignore

### 📚 문서
- [x] docs/ARCHITECTURE.md
- [x] docs/EVOLUTION_SYSTEM.md
- [x] docs/GROWTH_SYSTEM.md
- [x] docs/API.md
- [x] docs/CONTRIBUTING.md

### 🧪 예제 및 테스트
- [x] examples/ (5개 예제)
- [x] tests/ (테스트 파일)

### 🔧 빌드 및 패키징
- [ ] `python -m build` 실행 확인
- [ ] `pip install dist/babyhippo-*.whl` 테스트
- [ ] 버전 번호 확인 (pyproject.toml)

## 📝 릴리즈 노트 작성

### 릴리즈 제목
```
v4.3.0 - Cookiie v1.0 (1st Cookiie Revolution) 🍪
```

### 주요 변경사항
1. **Concept Neuron Selectivity** - 패턴 분리 강화
2. **Sleep/Consolidation/Recall Tuning** - 기억 정확도 향상
3. **Conversation Context Management** - 대화 맥락 관리
4. **Evolution System** - 생물학적 진화 순서 기반 성장 단계
5. **Blockchain Achievement** - 블록체인 기반 달성 시스템

### 설치 방법
```bash
pip install babyhippo
# 또는
pip install -e ".[all]"
```

### 빠른 시작
```python
from babyhippo.integration import CuriousBrain

cookiie = CuriousBrain(name="Cookiie")
response = cookiie.think("안녕하세요!")
print(response)
```

## 🎯 GitHub 릴리즈 생성 단계

1. **태그 생성**
   ```bash
   git tag -a v4.3.0 -m "Cookiie v1.0 - 1st Cookiie Revolution"
   git push origin v4.3.0
   ```

2. **릴리즈 페이지에서**
   - 제목: `v4.3.0 - Cookiie v1.0 (1st Cookiie Revolution) 🍪`
   - 설명: CHANGELOG.md의 v4.3.0 섹션 복사
   - 첨부 파일:
     - Source code (zip) - GitHub 자동 생성
     - Source code (tar.gz) - GitHub 자동 생성
     - (선택) wheel 파일 - `python -m build` 후 dist/ 폴더에서

3. **릴리즈 노트 작성**
   - 주요 기능
   - 변경사항
   - 설치 방법
   - 빠른 시작 예제

## 📦 패키지 빌드

```bash
# 빌드 도구 설치
pip install build

# 패키지 빌드
python -m build

# 결과물 확인
ls dist/
# babyhippo-4.3.0-py3-none-any.whl
# babyhippo-4.3.0.tar.gz
```

## ✅ 최종 확인

- [ ] 모든 테스트 통과
- [ ] 예제 실행 확인
- [ ] 문서 최신화
- [ ] 버전 번호 일치
- [ ] CHANGELOG.md 업데이트
- [ ] 릴리즈 노트 작성

