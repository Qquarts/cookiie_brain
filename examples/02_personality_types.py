#!/usr/bin/env python3
"""
BabyHippo 성격 유형 (DNA)
========================

이 예제는 다양한 성격 유형의 AI를 생성하고 비교합니다.

4가지 성격:
- 🦛 Quokka: 친화적, 호기심, 겁 많음
- 📚 Scholar: 분석적, 내향적, 지식 추구
- 🎩 Butler: 효율적, 충성, 과업 지향
- 💪 Athlete: 활동적, 에너지 넘침
"""

import sys
sys.path.insert(0, '..')

from babyhippo import BabyBrain, SpeciesType, DNA

def show_personality(species_name):
    """성격 특성을 표시합니다."""
    print(f"\n{'='*50}")
    
    # 종에 따른 이모지
    emojis = {
        "quokka": "🦛",
        "scholar": "📚",
        "butler": "🎩",
        "athlete": "💪"
    }
    emoji = emojis.get(species_name, "🧠")
    print(f"{emoji} {species_name.upper()}")
    print("="*50)
    
    # DNA 정보 출력
    species = SpeciesType[species_name.upper()]
    dna = DNA(species)
    
    # 주요 특성 출력
    print("\n📊 주요 특성:")
    
    # 욕구 가중치
    drives = dna.traits['drive_weights']
    print("\n  [욕구 가중치]")
    for key, value in drives.items():
        bar = "█" * int(value * 5) + "░" * (5 - int(value * 5))
        print(f"    {key:15}: {bar} ({value:.1f})")
    
    # 감정 편향
    emotions = dna.traits['emotional_bias']
    print("\n  [감정 편향]")
    for key, value in emotions.items():
        bar = "█" * int(value * 5) + "░" * (5 - int(value * 5))
        print(f"    {key:15}: {bar} ({value:.1f})")
    
    # 반사 패턴
    reflexes = dna.traits['reflex_patterns']
    print("\n  [반사 패턴]")
    for trigger, response in reflexes[:3]:
        print(f"    '{trigger}' → '{response}'")
    
    # 간단한 대화 테스트
    print("\n💬 대화 테스트:")
    brain = BabyBrain(name=f"Test{species_name}", species=species_name)
    
    test_inputs = ["안녕!", "뭐해?"]
    for inp in test_inputs:
        response = brain.chat(inp)
        print(f"    Q: {inp}")
        print(f"    A: {response}")


def main():
    print("\n" + "="*60)
    print("🧬 BabyHippo 성격 유형 비교")
    print("="*60)
    
    # 각 성격 유형 테스트
    for species in ["quokka", "scholar", "butler", "athlete"]:
        show_personality(species)
    
    print("\n" + "="*60)
    print("✅ 성격 유형 비교 완료!")
    print("="*60)


if __name__ == "__main__":
    main()

