#!/usr/bin/env python3
"""
BabyHippo 기본 사용법
====================

이 예제는 BabyHippo의 가장 기본적인 사용법을 보여줍니다.

실행 방법:
    python3 01_basic_usage.py
"""

import sys
sys.path.insert(0, '..')  # 패키지 경로 추가

from babyhippo import BabyBrain

def main():
    print("=" * 60)
    print("🧠 BabyHippo 기본 사용법")
    print("=" * 60)
    
    # 1. 뇌 생성
    print("\n📦 1. 뇌 생성")
    brain = BabyBrain(name="MyAI", species="quokka")
    print(f"   ✅ '{brain.name}' 생성 완료!")
    
    # 2. 학습
    print("\n📚 2. 학습")
    brain.learn("내 이름은 BabyHippo입니다")
    brain.learn("저는 새로운 것을 배우는 걸 좋아해요")
    brain.learn("파이썬은 프로그래밍 언어입니다")
    print("   ✅ 3개 항목 학습 완료!")
    
    # 3. 대화
    print("\n💬 3. 대화")
    questions = [
        "안녕!",
        "이름이 뭐야?",
        "파이썬이 뭐야?"
    ]
    
    for q in questions:
        response = brain.chat(q)
        print(f"   Q: {q}")
        print(f"   A: {response}")
        print()
    
    # 4. 상태 확인
    print("\n📊 4. 상태 확인")
    status = brain.get_status()
    print(f"   에너지: {status.get('energy', 'N/A'):.0%}")
    print(f"   기분: {status.get('mood', 'N/A')}")
    
    # 5. 기억 회상
    print("\n🔍 5. 기억 회상")
    memories = brain.recall("파이썬")
    if memories:
        print(f"   '파이썬' 관련 기억 {len(memories)}개 발견:")
        for mem in memories[:3]:
            content = mem.get('content', mem.get('word', 'N/A'))
            score = mem.get('score', mem.get('weight', 0))
            print(f"   - {content} (점수: {score:.2f})")
    else:
        print("   기억 없음")
    
    # 6. 수면 (기억 공고화)
    print("\n🌙 6. 수면 (기억 공고화)")
    result = brain.sleep(hours=2, verbose=True)
    print(f"   {result}")
    
    # 7. 저장
    print("\n💾 7. 상태 저장")
    try:
        brain.save()
        print("   ✅ 저장 완료!")
    except Exception as e:
        print(f"   ⚠️ 저장 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 예제 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

