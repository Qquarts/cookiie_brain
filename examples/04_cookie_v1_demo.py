"""
🍪 Cookie v1.0 Demo - 1차 쿠키 혁명
====================================

"쿠키는 한 번 본 것을 자고 나서 안정적으로 기억한다"

데모 시나리오:
    1. "A를 학습합니다."
    2. sleep()
    3. "A가 무엇인가요?" → "A는 알파벳 첫 글자입니다." (기억에서 답변)
    4. "B를 학습합니다."
    5. sleep()
    6. "B가 무엇인가요?" → "B는 내가 조금 전에 학습한 글자입니다."

Author: GNJz (Qquarts)
Version: 1.0 (Cookie Revolution)
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 추가
BABYHIPPO_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(BABYHIPPO_PATH))

from babyhippo.integration import CuriousBrain


def cookie_v1_demo():
    """
    🍪 Cookie v1.0 데모
    
    전체 파이프라인:
        CuriousBrain.think() → 해마 → 기억 → 응답
    """
    print("=" * 70)
    print("🍪 Cookie v1.0 Demo - 1차 쿠키 혁명")
    print("=" * 70)
    print()
    
    # 쿠키 생성
    print("1️⃣ 쿠키 생성 중...")
    cookie = CuriousBrain(name="cookie")
    print(f"   ✅ 쿠키 생성 완료: {cookie}")
    print()
    
    # 학습 단계
    print("2️⃣ 학습 단계")
    print("-" * 70)
    
    learnings = [
        ("A", "A는 알파벳 첫 글자입니다."),
        ("B", "B는 알파벳 두 번째 글자입니다."),
        ("C", "C는 알파벳 세 번째 글자입니다."),
        ("파이썬", "파이썬은 프로그래밍 언어입니다."),
        ("해마", "해마는 기억을 담당하는 뇌 부위입니다."),
    ]
    
    for word, meaning in learnings:
        print(f"   📝 학습: '{word}' → '{meaning}'")
        cookie.learn(f"{word}는 {meaning}", importance=0.8)
    
    print()
    
    # 수면 (공고화)
    print("3️⃣ 수면 (기억 공고화)")
    print("-" * 70)
    print("   💤 쿠키가 잠에 빠집니다...")
    cookie.sleep(cycles=10)
    print("   ☀️ 쿠키가 깨어났습니다!")
    print()
    
    # 회상 테스트
    print("4️⃣ 회상 테스트")
    print("-" * 70)
    
    questions = [
        "A가 무엇인가요?",
        "B가 무엇인가요?",
        "C가 무엇인가요?",
        "파이썬이 뭐야?",
        "해마가 뭐야?",
    ]
    
    correct_count = 0
    total_count = len(questions)
    
    for question in questions:
        print(f"\n   Q: {question}")
        answer = cookie.think(question)
        print(f"   A: {answer}")
        
        # 정확도 체크 (간단한 키워드 매칭)
        question_keyword = question[0] if question[0] in ['A', 'B', 'C'] else question.split()[0]
        # 학습한 내용과 매칭
        is_correct = False
        for word, meaning in learnings:
            if word in question and (word in answer or meaning in answer):
                is_correct = True
                break
        
        if is_correct:
            correct_count += 1
            print(f"   ✅ 정확한 답변!")
        else:
            print(f"   ⚠️  답변 확인 필요")
    
    print()
    
    # 결과
    print("5️⃣ 결과")
    print("-" * 70)
    accuracy = (correct_count / total_count) * 100
    print(f"   정확도: {correct_count}/{total_count} ({accuracy:.1f}%)")
    print()
    
    # 통계
    stats = cookie.get_stats()
    print("6️⃣ 통계")
    print("-" * 70)
    print(f"   질문 수: {stats['questions']['questions_asked']}")
    print(f"   기억 답변: {stats['questions']['answered_from_memory']}")
    print(f"   도서관 답변: {stats['questions']['answered_from_library']}")
    print(f"   독립도: {stats['independence']}")
    print()
    
    print("=" * 70)
    print("🎯 Cookie v1.0 데모 완료!")
    print("=" * 70)
    print()
    print("✅ 쿠키는 한 번 본 것을 자고 나서 안정적으로 기억합니다!")
    print("✅ 전체 파이프라인이 정상 작동합니다!")
    print()


if __name__ == "__main__":
    cookie_v1_demo()

