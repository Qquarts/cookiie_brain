#!/usr/bin/env python3
"""
BabyHippo Robot Runner
======================

뇌(BabyBrain)와 몸(NervousSystem)을 연결하여
실제 로봇처럼 작동하는 통합 실행 파일

Usage:
    python run_robot.py
    python run_robot.py --species scholar
    python run_robot.py --voice  # TTS 활성화

Author: GNJz (Qquarts)
Version: 1.0
"""

import sys
import time
import argparse

# babyhippo 모듈 임포트
from babyhippo.integration import BabyBrain
from babyhippo.body import NervousSystem, Senses, Actions
from babyhippo.body.senses import SensorType


def main():
    # 인자 파싱
    parser = argparse.ArgumentParser(description='BabyHippo Robot Runner')
    parser.add_argument('--name', default='QuokkaBot', help='로봇 이름')
    parser.add_argument('--species', default='quokka', 
                        choices=['quokka', 'scholar', 'butler', 'athlete'],
                        help='성격 유형')
    parser.add_argument('--voice', action='store_true', help='TTS 활성화')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 BabyHippo Robot System v1.0")
    print("=" * 60)
    print(f"\n🚀 부팅 중... (성격: {args.species})")
    
    # =========================================================
    # 1. 뇌 생성
    # =========================================================
    brain = BabyBrain(
        name=args.name,
        species=args.species,
        auto_save=True
    )
    
    # =========================================================
    # 2. 신경계(몸) 생성 및 뇌 연결
    # =========================================================
    body = NervousSystem(brain=brain)
    
    # =========================================================
    # 3. 감각/운동 기관 활성화
    # =========================================================
    print("\n📡 장치 활성화 중...")
    status = body.activate()
    
    for device, active in status.items():
        icon = "✅" if active else "❌"
        print(f"   {icon} {device}")
    
    # TTS 활성화 (옵션)
    if args.voice:
        body.actions.speech.activate()
        print("   ✅ TTS (음성 출력)")
    
    # =========================================================
    # 4. 모니터링 시작 (배터리, 온도 등)
    # =========================================================
    body.start_monitoring(interval=5.0)  # 5초마다 체크
    
    # =========================================================
    # 5. 초기 학습
    # =========================================================
    print("\n📚 초기 학습 중...")
    brain.learn(f"제 이름은 {args.name}입니다.", importance=0.9)
    brain.learn("저는 BabyHippo 기반 AI 로봇이에요.", importance=0.8)
    
    # =========================================================
    # 6. 메인 루프
    # =========================================================
    print("\n" + "=" * 60)
    print("🎉 시스템 준비 완료!")
    print("=" * 60)
    print("""
📋 명령어:
    - 텍스트 입력  →  일반 대화
    - '듣기'       →  음성 인식 (5초)
    - '보기'       →  카메라 캡처
    - '상태'       →  시스템 상태 확인
    - '자'         →  수면 모드 (기억 공고화)
    - 'exit'       →  종료
    """)
    
    try:
        while True:
            # 사용자 입력 대기
            try:
                user_input = input("\n👤 You: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            # ----- 명령어 처리 -----
            
            if user_input.lower() == 'exit':
                print("\n🛑 종료 중...")
                break
            
            elif user_input == '듣기':
                # 청각 입력 테스트
                print("👂 듣는 중... (5초)")
                response = body.receive_input(SensorType.AUDITORY)
                if response:
                    print(f"\n🤖 {args.name}: {response}")
                else:
                    print("   (음성 인식 실패 또는 마이크 비활성)")
            
            elif user_input == '보기':
                # 시각 입력 테스트
                print("👁️ 보는 중...")
                raw = body.senses.sense(SensorType.VISUAL)
                if raw:
                    print(f"   📷 캡처 완료: {raw.metadata}")
                else:
                    print("   (카메라 비활성)")
            
            elif user_input == '상태':
                # 시스템 상태 출력
                print(body.get_full_status())
                print(brain.status())
            
            elif user_input in ['자', '잠', '수면', 'sleep']:
                # 수면 모드
                print("\n💤 수면 모드 진입...")
                body.sleep()
                result = brain.sleep(hours=1, verbose=True)
                body.wake()
                print(f"\n☀️ 기상! {result}")
            
            else:
                # ----- 일반 대화 -----
                response = body.process(user_input)
                
                if response and response != "...":
                    print(f"\n🤖 {args.name}: {response}")
                    
                    # TTS 출력 (활성화 시)
                    if args.voice and body.actions.speech.is_active:
                        body.actions.speech.speak(response)
            
            # ----- 생명 활동 (1틱) -----
            # 시상하부 업데이트 (에너지, 욕구 등)
            brain.hypothalamus.tick(action_type='chat', stimulus_level=0.5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Ctrl+C 감지, 종료 중...")
    
    finally:
        # =========================================================
        # 7. 정리
        # =========================================================
        print("\n💾 상태 저장 중...")
        brain.save()
        
        print("🔌 장치 비활성화 중...")
        body.deactivate()
        
        print("\n👋 안녕히 가세요!")
        print("=" * 60)


if __name__ == "__main__":
    main()

