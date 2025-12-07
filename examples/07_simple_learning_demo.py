#!/usr/bin/env python3
"""
🍪 Cookiie 간단한 학습 데모

4단계 학습 프로세스를 간단하게 시뮬레이션합니다.

실행 방법:
    python3 examples/07_simple_learning_demo.py
    또는
    ./run_demo.sh simple
"""

import sys
from pathlib import Path

# 경로 설정
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from babyhippo.integration import CuriousBrain


def main():
    print("=" * 70)
    print("🍪 Cookiie 간단한 학습 데모")
    print("=" * 70)
    print()
    
    # Cookiie 생성
    cookiie = CuriousBrain(name="Cookiie")
    print(f"✅ Cookiie 생성 완료\n")
    
    # =================================================================
    # 1단계: 개념 뉴런 생성
    # =================================================================
    print("1️⃣ 개념 뉴런 생성")
    print("-" * 70)
    
    concepts = ["사과", "빨간색", "달다"]
    for concept in concepts:
        print(f"   학습: {concept}")
        cookiie.learn(concept, importance=0.8)
        print(f"   ✅ 저장됨")
    print()
    
    # =================================================================
    # 2단계: 연결 형성
    # =================================================================
    print("2️⃣ 연결 형성 (STDP)")
    print("-" * 70)
    
    associations = [
        "사과는 빨간색",
        "사과는 빨간색",  # 반복으로 강화
        "사과는 달다",
    ]
    
    for assoc in associations:
        print(f"   학습: {assoc}")
        cookiie.learn(assoc, importance=0.8)
        print(f"   ✅ 연결 강화됨")
    print()
    
    # =================================================================
    # 3단계: 수면
    # =================================================================
    print("3️⃣ 수면 공고화")
    print("-" * 70)
    print("   💤 수면 중...")
    cookiie.sleep(cycles=3)
    print("   ✅ 수면 완료\n")
    
    # =================================================================
    # 4단계: 회상 테스트
    # =================================================================
    print("4️⃣ 회상 테스트")
    print("-" * 70)
    
    questions = [
        "사과는 무슨 색이야?",
        "사과는 어떤 맛이야?",
    ]
    
    for question in questions:
        print(f"   Q: {question}")
        answer = cookiie.think(question)
        print(f"   A: {answer}")
        print()
    
    print("=" * 70)
    print("✅ 학습 시뮬레이션 완료!")
    print("=" * 70)


if __name__ == "__main__":
    main()

