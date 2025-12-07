"""
🍪 Cookiie v1.0 - 대화형 인터페이스
==================================

쿠키와 직접 대화해보세요!

사용법:
    python examples/05_cookiie_interactive.py

명령어:
    - "학습: [내용]" - 새로운 내용 학습
    - "수면" - 기억 공고화
    - "통계" - 쿠키 상태 확인
    - "종료" 또는 "exit" - 프로그램 종료
    - 그 외 - 질문 (쿠키가 답변)

예시:
    > 학습: 파이썬은 프로그래밍 언어입니다.
    > 수면
    > 파이썬이 뭐야?
    > 통계

Author: GNJz (Qquarts)
Version: 1.0 (Cookiie Interactive)
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 추가
BABYHIPPO_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(BABYHIPPO_PATH))

from babyhippo.integration import CuriousBrain


def main():
    """
    🍪 Cookiie v1.0 대화형 인터페이스
    """
    print("=" * 70)
    print("🍪 Cookiie v1.0 - 대화형 인터페이스")
    print("=" * 70)
    print()
    print("쿠키를 생성하는 중...")
    
    # 쿠키 생성
    cookiie = CuriousBrain(name="cookiie")
    
    print(f"✅ 쿠키 생성 완료!")
    print()
    print("📋 사용법:")
    print("   - '학습: [내용]' - 새로운 내용 학습")
    print("   - '수면' - 기억 공고화")
    print("   - '통계' - 쿠키 상태 확인")
    print("   - '종료' 또는 'exit' - 프로그램 종료")
    print("   - 그 외 - 질문 (쿠키가 답변)")
    print()
    print("=" * 70)
    print()
    
    # 대화 루프
    while True:
        try:
            # 사용자 입력
            user_input = input("👤 당신: ").strip()
            
            if not user_input:
                continue
            
            # 명령어 처리
            if user_input.lower() in ['종료', 'exit', 'quit', 'q']:
                print("\n👋 쿠키: 안녕히 가세요! 좋은 하루 되세요! 😊")
                break
            
            elif user_input == '수면':
                print("\n💤 쿠키가 잠에 빠집니다...")
                cookiie.sleep(cycles=10)
                print("☀️ 쿠키가 깨어났습니다!")
                print()
                continue
            
            elif user_input in ['통계', '상태', 'state', 'status']:
                stats = cookiie.get_stats()
                growth_stage = stats.get('growth_stage', 'BabyHippo')
                
                print("\n📊 쿠키 상태:")
                print("-" * 70)
                print(f"   이름: {stats.get('name', 'cookiie')}")
                print(f"   성장 단계: {growth_stage} 🦛")
                print(f"   버전: BabyHippo v4.3.0")
                print(f"   질문 수: {stats['questions']['questions_asked']}")
                print(f"   기억 답변: {stats['questions']['answered_from_memory']}")
                print(f"   도서관 답변: {stats['questions']['answered_from_library']}")
                print(f"   독립도: {stats['independence']}")
                print(f"   지식 수: {stats['knowledge_count']}")
                if 'brain' in stats:
                    brain_stats = stats['brain']
                    if 'hippo' in brain_stats:
                        memory_count = brain_stats['hippo'].get('word_count', 0)
                        print(f"   기억 수: {memory_count}개")
                        # 🦛 성장 단계 힌트
                        if growth_stage == 'BabyHippo':
                            print(f"   → 다음 단계: TeenHippo (100개 기억 필요)")
                        elif growth_stage == 'TeenHippo':
                            print(f"   → 다음 단계: Hippocampus (1000개 기억 필요)")
                        elif growth_stage == 'Hippocampus':
                            print(f"   → 다음 단계: WisdomHippo (10000개 기억 필요)")
                        elif growth_stage == 'WisdomHippo':
                            print(f"   → 다음 단계: MagicHippo (100000개 기억 필요)")
                        elif growth_stage == 'MagicHippo':
                            print(f"   → 신의 경지 달성! ✨")
                print()
                # 🦛 성장 단계 표시
                print(f"🍪 Cookiie state: {growth_stage} (BabyHippo v4.3.0)")
                print()
                continue
            
            elif user_input.startswith('학습:'):
                # 학습 명령
                content = user_input[3:].strip()
                if content:
                    print(f"\n📝 학습 중: '{content}'")
                    cookiie.learn(content, importance=0.8)
                    print("✅ 학습 완료!")
                    print()
                else:
                    print("⚠️  학습할 내용을 입력해주세요. (예: 학습: 파이썬은 프로그래밍 언어입니다.)")
                    print()
                continue
            
            # 🍪 v1.0: 자연어 학습 명령 자동 감지
            # 🛑 치명적 충돌 해결 v2: 질문 필터링 최우선 적용
            # 질문이면 절대 학습 경로로 가지 않음
            elif cookiie._is_question_strict(user_input):
                # 질문이면 답변 경로로 (아래 일반 질문 처리로 넘어감)
                pass
            else:
                # 질문이 아닐 때만 학습 명령 패턴 체크
                learning_patterns = [
                    '라고 해', '라고 해요', '라고 합니다',
                    '기억해', '기억해줘', '기억해요',
                    '알아둬', '알아둬요',
                ]
                
                # 이름 소개 패턴 (실제 내용이 있어야 함)
                name_intro_patterns = ['내 이름은', '나는', '저는', '내가', '제가']
                has_name_intro = any(pattern in user_input for pattern in name_intro_patterns)
                
                # 실제 내용이 있는지 확인
                has_actual_content = False
                if has_name_intro:
                    for pattern in name_intro_patterns:
                        if pattern in user_input:
                            after_pattern = user_input.split(pattern, 1)[-1].strip()
                            if after_pattern and len(after_pattern) > 0:
                                # 질문 마커나 의문사가 없어야 함
                                if not any(q in after_pattern for q in ['?', '뭐', '무엇', '뭐야', '무엇이야', '기억나']):
                                    if len(after_pattern.replace(' ', '')) > 0:
                                        has_actual_content = True
                            break
                
                # 학습 명령 감지
                is_learning_command = (
                    any(pattern in user_input for pattern in learning_patterns) or
                    (has_name_intro and has_actual_content)
                )
                
                if is_learning_command:
                    # 자연어 학습 명령 감지
                    print(f"\n📝 학습 중: '{user_input}'")
                    cookiie.learn(user_input, importance=0.8)
                    print("✅ 학습 완료! (자동 감지)")
                    print()
                    continue
            
            # 일반 질문
            print()
            answer = cookiie.think(user_input)
            print(f"🍪 쿠키: {answer}")
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 쿠키: 안녕히 가세요! 좋은 하루 되세요! 😊")
            break
        except Exception as e:
            print(f"\n⚠️  오류 발생: {e}")
            print("   계속 진행합니다...")
            print()


if __name__ == "__main__":
    main()

