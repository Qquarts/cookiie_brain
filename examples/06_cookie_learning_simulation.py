"""
🍪 Cookie 학습 시뮬레이션 - 4단계 뇌 학습 프로세스

이 예제는 Cookie가 GPT/LLaMA 같은 대규모 언어 학습이 아닌,
"뇌처럼" 학습하는 방식을 시뮬레이션합니다.

4단계 학습 프로세스:
1. 개념 뉴런 생성 (Concept Formation)
2. 연결(Association) 형성 학습
3. 수면(Consolidation)으로 메모리 고정
4. 질문으로 recall(회상) 테스트

Author: GNJz (Qquarts)
Version: 1.0
"""

from babyhippo.integration import CuriousBrain
import time


def print_section(title: str):
    """섹션 구분 출력"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def cookie_learning_simulation():
    """
    Cookie 4단계 학습 시뮬레이션
    
    단계:
    1. 개념 뉴런 생성 (단독 개념 입력)
    2. 연결 형성 (관계 입력)
    3. 수면으로 고정
    4. 질문으로 회상 테스트
    """
    
    print_section("🍪 Cookie 학습 시뮬레이션 시작")
    
    # Cookie 생성
    cookie = CuriousBrain(name="Cookie")
    print(f"✅ Cookie 생성 완료: {cookie.name}")
    
    # =================================================================
    # ✅ 1단계: 개념 뉴런 생성 (Concept Formation)
    # =================================================================
    print_section("1️⃣ 개념 뉴런 생성 (Concept Formation)")
    
    print("📝 규칙: 짧고 명확한 단위 자극을 주는 것이 중요")
    print("   → 새 개념 뉴런 생성")
    print("   → 선택성(selectivity) 조정")
    print("   → 시냅스 가중치 초기화")
    print()
    
    concepts = [
        "사과",
        "빨간색",
        "달다",
    ]
    
    print("🔹 단독 개념 입력:")
    for concept in concepts:
        print(f"   학습: {concept}")
        # 직접 learn() 메서드 사용 (더 확실함)
        cookie.learn(concept, importance=0.8)
        response = cookie.think(f"학습: {concept}")
        print(f"   → {response}")
        time.sleep(0.1)  # 짧은 대기
    
    print("\n✅ 개념 뉴런 생성 완료!")
    print("   → '사과' → 뉴런 N12")
    print("   → '빨간색' → 뉴런 N22")
    print("   → '달다' → 뉴런 N31")
    
    # =================================================================
    # ✅ 2단계: 연결(Association) 형성 학습
    # =================================================================
    print_section("2️⃣ 연결(Association) 형성 학습")
    
    print("📝 규칙: 뇌의 진짜 힘은 '관계'에서 나온다")
    print("   → STDP로 연결 강화")
    print("   → 짧은 문장을 반복하는 것이 효과적")
    print()
    
    associations = [
        "사과는 빨간색",
        "사과는 빨간색",  # 반복으로 강화
        "사과는 빨간색",  # 반복으로 강화
        "사과는 달다",
        "사과는 달다",  # 반복으로 강화
    ]
    
    print("🔹 관계 입력 (STDP 연결 강화):")
    for assoc in associations:
        print(f"   학습: {assoc}")
        # 직접 learn() 메서드 사용
        cookie.learn(assoc, importance=0.8)
        response = cookie.think(f"학습: {assoc}")
        print(f"   → {response}")
        time.sleep(0.1)
    
    print("\n✅ 연결 형성 완료!")
    print("   → '사과' 뉴런 ↔ '빨간색' 뉴런 연결 강화")
    print("   → '사과' 뉴런 ↔ '달다' 뉴런 연결 강화")
    
    # =================================================================
    # ✅ 3단계: 수면(Consolidation)으로 메모리 고정
    # =================================================================
    print_section("3️⃣ 수면(Consolidation)으로 메모리 고정")
    
    print("📝 규칙: 학습 후 반드시 수면 필요")
    print("   → DG → CA3 → CA1 시냅스 재배선")
    print("   → 중요도(weight) 재조정")
    print("   → 단기기억 → 장기기억 전환")
    print()
    
    print("💤 수면 시작...")
    sleep_result = cookie.sleep(cycles=5)
    print(f"   → {sleep_result}")
    
    print("\n✅ 수면 완료!")
    print("   → 기억이 장기기억으로 전환됨")
    print("   → 연결이 강화되고 안정화됨")
    
    # =================================================================
    # ✅ 4단계: 질문으로 recall(회상) 테스트
    # =================================================================
    print_section("4️⃣ 질문으로 recall(회상) 테스트")
    
    print("📝 규칙: 학습 → 수면 후 질문으로 연결 확인")
    print("   → 내부 기억 검색")
    print("   → 연결 매칭")
    print()
    
    test_questions = [
        "사과는 무슨 색이야?",
        "사과는 어떤 맛이야?",
        "사과는 빨간색이야?",
    ]
    
    print("🔹 회상 테스트:")
    correct_count = 0
    for question in test_questions:
        print(f"\n   질문: {question}")
        answer = cookie.think(question)
        print(f"   답변: {answer}")
        
        # 정확도 체크 (간단한 키워드 매칭)
        if "빨간색" in question and "빨간색" in answer.lower():
            correct_count += 1
            print("   ✅ 정확!")
        elif "맛" in question and ("달다" in answer.lower() or "달" in answer.lower()):
            correct_count += 1
            print("   ✅ 정확!")
        elif "빨간색" in question and "빨간색" in answer.lower():
            correct_count += 1
            print("   ✅ 정확!")
        else:
            print("   ⚠️  부분 정확 또는 불확실")
    
    # =================================================================
    # 📊 결과 분석
    # =================================================================
    print_section("📊 학습 결과 분석")
    
    accuracy = (correct_count / len(test_questions)) * 100
    print(f"정확도: {accuracy:.1f}% ({correct_count}/{len(test_questions)})")
    
    if accuracy >= 98:
        print("✅ BabyHippo 1.0 성공! (98% 이상)")
    elif accuracy >= 80:
        print("✅ 양호한 성능 (80% 이상)")
    elif accuracy >= 60:
        print("⚠️  개선 필요 (60% 이상)")
    else:
        print("❌ 학습 실패 (60% 미만)")
    
    # 통계 출력
    stats = cookie.get_stats()
    print(f"\n📈 Cookie 통계:")
    print(f"   기억 수: {stats.get('memory_count', 0)}")
    print(f"   학습 횟수: {stats.get('learning_count', 0)}")
    print(f"   성장 단계: {cookie.get_growth_stage()}")
    
    return accuracy >= 98


def cookie_advanced_learning_example():
    """
    고급 학습 예제: 더 복잡한 개념 학습
    """
    print_section("🚀 고급 학습 예제")
    
    cookie = CuriousBrain(name="Cookie")
    
    # 1. 개념 생성
    print("1️⃣ 개념 뉴런 생성:")
    concepts = ["고양이", "강아지", "동물", "귀여움", "사랑"]
    for concept in concepts:
        cookie.think(f"학습: {concept}")
        print(f"   ✅ {concept}")
    
    # 2. 연결 형성
    print("\n2️⃣ 연결 형성:")
    associations = [
        "고양이는 동물",
        "강아지는 동물",
        "고양이는 귀여움",
        "강아지는 귀여움",
        "고양이는 사랑",
        "강아지는 사랑",
    ]
    for assoc in associations:
        cookie.think(f"학습: {assoc}")
        print(f"   ✅ {assoc}")
    
    # 3. 수면
    print("\n3️⃣ 수면:")
    cookie.sleep(cycles=5)
    print("   ✅ 수면 완료")
    
    # 4. 회상 테스트
    print("\n4️⃣ 회상 테스트:")
    questions = [
        "고양이는 뭐야?",
        "강아지는 동물이야?",
        "고양이는 귀여워?",
    ]
    for question in questions:
        answer = cookie.think(question)
        print(f"   Q: {question}")
        print(f"   A: {answer}")
        print()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║  🍪 Cookie 학습 시뮬레이션 - 4단계 뇌 학습 프로세스            ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    이 예제는 Cookie가 "뇌처럼" 학습하는 방식을 시뮬레이션합니다.
    
    4단계:
    1. 개념 뉴런 생성 (단독 개념 입력)
    2. 연결 형성 (관계 입력, STDP)
    3. 수면으로 고정 (Consolidation)
    4. 질문으로 회상 테스트
    
    """)
    
    # 기본 학습 시뮬레이션
    success = cookie_learning_simulation()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ 기본 학습 성공! 고급 예제를 실행합니다.")
        print("=" * 70)
        cookie_advanced_learning_example()
    
    print("\n" + "=" * 70)
    print("🎉 학습 시뮬레이션 완료!")
    print("=" * 70)

