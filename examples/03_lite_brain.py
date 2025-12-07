#!/usr/bin/env python3
"""
LiteBrain - 저전력 엣지 디바이스용
=================================

이 예제는 라즈베리파이 같은 저전력 기기에서
LLM 없이 동작하는 LiteBrain을 보여줍니다.

특징:
- LLM API 불필요
- 패턴 기반 학습
- 최소 메모리 사용
- 빠른 응답
"""

import sys
sys.path.insert(0, '..')

from babyhippo import LiteBrain

def main():
    print("=" * 60)
    print("🔋 LiteBrain - 저전력 모드")
    print("=" * 60)
    
    # 1. LiteBrain 생성
    print("\n📦 1. LiteBrain 생성")
    brain = LiteBrain(name="EdgeAI", capacity=500)
    print(f"   ✅ '{brain.name}' 생성 완료! (용량: 500)")
    
    # 2. 패턴 학습
    print("\n📚 2. 패턴 학습")
    patterns = [
        ("안녕", "안녕하세요! 반가워요 😊"),
        ("이름", "저는 EdgeAI예요!"),
        ("날씨", "오늘 날씨가 좋아요! ☀️"),
        ("뭐해", "대화하고 있어요! 💬"),
        ("고마워", "천만에요! 😊"),
        ("잘가", "안녕히 가세요! 👋"),
        ("사랑", "저도 좋아해요! ❤️"),
        ("피곤", "좀 쉬세요~ 🛋️"),
    ]
    
    for trigger, response in patterns:
        brain.learn(trigger, response)
        print(f"   학습: '{trigger}' → '{response}'")
    
    # 3. 대화 테스트
    print("\n💬 3. 대화 테스트")
    test_inputs = [
        "안녕!",
        "네 이름이 뭐야?",
        "오늘 날씨 어때?",
        "뭐하고 있어?",
        "도와줘서 고마워",
        "잘가~",
        "모르는 질문이야"  # 학습되지 않은 패턴
    ]
    
    for inp in test_inputs:
        response = brain.chat(inp)
        print(f"   Q: {inp}")
        print(f"   A: {response}")
        print()
    
    # 4. 메모리 상태
    print("\n📊 4. 메모리 상태")
    stats = brain.get_stats()
    print(f"   학습된 패턴: {stats.get('patterns', 'N/A')}개")
    print(f"   대화 횟수: {stats.get('conversations', 'N/A')}")
    print(f"   기억 사용량: {stats.get('memory_used', 'N/A')}")
    
    # 5. 저장
    print("\n💾 5. 저장")
    try:
        brain.save("lite_brain_state.json")
        print("   ✅ lite_brain_state.json 저장 완료!")
    except Exception as e:
        print(f"   ⚠️ 저장 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ LiteBrain 예제 완료!")
    print("=" * 60)
    print("\n💡 Tip: LiteBrain은 라즈베리파이, Arduino 등")
    print("   저전력 기기에서 LLM 없이 동작합니다.")


if __name__ == "__main__":
    main()

