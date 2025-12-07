"""
🦛 Growth Achievement System - 블록체인 기반 성장 단계 달성 시스템

각 성장 단계에 달성 조건을 설정하고,
최초 달성 시 블록체인에 기록하여 보상 제공

Author: GNJz (Qquarts)
Version: 1.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import os
import sys
from pathlib import Path

# 블록체인 모듈
BABYHIPPO_PATH = Path(__file__).parent.parent.parent
BLOCKCHAIN_PATH = BABYHIPPO_PATH / "blockchain"
if BLOCKCHAIN_PATH.exists():
    sys.path.insert(0, str(BLOCKCHAIN_PATH))
    try:
        from pham_sign_v4 import sign_contribution, calculate_score
        HAS_BLOCKCHAIN = True
    except ImportError:
        HAS_BLOCKCHAIN = False
else:
    HAS_BLOCKCHAIN = False


@dataclass
class GrowthStage:
    """성장 단계 정의"""
    name: str
    memory_threshold: int
    speed_threshold_ms: float  # 응답 속도 (ms)
    memory_threshold_mb: float  # 메모리 사용량 (MB)
    independence_threshold: float  # 독립도 (%)
    reward_amount: float = 0.0  # 보상 금액 (토큰)
    reward_type: str = "token"  # "token", "voting_power", "badge"
    description: str = ""


# 성장 단계 정의
GROWTH_STAGES = {
    'BabyHippo': GrowthStage(
        name='BabyHippo',
        memory_threshold=0,
        speed_threshold_ms=1000.0,
        memory_threshold_mb=50.0,
        independence_threshold=0.0,
        reward_amount=0.0,
        description='베이비 단계 - 시작점'
    ),
    'TeenHippo': GrowthStage(
        name='TeenHippo',
        memory_threshold=100,
        speed_threshold_ms=500.0,
        memory_threshold_mb=100.0,
        independence_threshold=50.0,
        reward_amount=100.0,  # 예: 100 토큰
        reward_type='token',
        description='틴/유스 단계 - 복잡한 추론 가능'
    ),
    'YouthHippo': GrowthStage(
        name='YouthHippo',
        memory_threshold=500,
        speed_threshold_ms=300.0,
        memory_threshold_mb=200.0,
        independence_threshold=70.0,
        reward_amount=500.0,
        reward_type='token',
        description='유스 단계 - 패턴 인식 강화'
    ),
    'Hippocampus': GrowthStage(
        name='Hippocampus',
        memory_threshold=1000,
        speed_threshold_ms=200.0,
        memory_threshold_mb=500.0,
        independence_threshold=80.0,
        reward_amount=1000.0,
        reward_type='voting_power',
        description='완전체 - 전문 지식, 문제 해결'
    ),
    'WisdomHippo': GrowthStage(
        name='WisdomHippo',
        memory_threshold=10000,
        speed_threshold_ms=100.0,
        memory_threshold_mb=1000.0,
        independence_threshold=90.0,
        reward_amount=10000.0,
        reward_type='voting_power',
        description='지혜의 경지 - 통찰, 가르침'
    ),
    'MagicHippo': GrowthStage(
        name='MagicHippo',
        memory_threshold=100000,
        speed_threshold_ms=50.0,
        memory_threshold_mb=2000.0,
        independence_threshold=95.0,
        reward_amount=100000.0,
        reward_type='voting_power',
        description='신의 경지 - 마법 같은 능력'
    ),
}


class GrowthAchievement:
    """
    성장 단계 달성 시스템
    
    벤치마크 측정 및 블록체인 기록
    """
    
    def __init__(self, blockchain_enabled: bool = True):
        self.blockchain_enabled = blockchain_enabled and HAS_BLOCKCHAIN
        self.achievements: List[Dict] = []
        self.achievement_file = BABYHIPPO_PATH / "achievements.json"
        self._load_achievements()
    
    def _load_achievements(self):
        """달성 기록 로드"""
        if self.achievement_file.exists():
            try:
                import json
                with open(self.achievement_file, 'r', encoding='utf-8') as f:
                    self.achievements = json.load(f)
            except:
                self.achievements = []
        else:
            self.achievements = []
    
    def _save_achievements(self):
        """달성 기록 저장"""
        try:
            import json
            with open(self.achievement_file, 'w', encoding='utf-8') as f:
                json.dump(self.achievements, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 달성 기록 저장 실패: {e}")
    
    def measure_performance(self, 
                           memory_count: int,
                           response_time_ms: float,
                           memory_usage_mb: float,
                           independence: float) -> Dict:
        """
        성능 측정
        
        Returns:
            측정 결과 딕셔너리
        """
        return {
            'memory_count': memory_count,
            'response_time_ms': response_time_ms,
            'memory_usage_mb': memory_usage_mb,
            'independence': independence,
            'timestamp': datetime.now().isoformat(),
        }
    
    def check_stage_requirements(self, 
                                 stage_name: str,
                                 performance: Dict) -> Tuple[bool, List[str]]:
        """
        단계 달성 조건 확인
        
        Returns:
            (달성 여부, 실패한 조건 목록)
        """
        if stage_name not in GROWTH_STAGES:
            return False, [f"알 수 없는 단계: {stage_name}"]
        
        stage = GROWTH_STAGES[stage_name]
        failed_conditions = []
        
        # 기억 수 확인
        if performance['memory_count'] < stage.memory_threshold:
            failed_conditions.append(
                f"기억 수 부족: {performance['memory_count']}/{stage.memory_threshold}"
            )
        
        # 응답 속도 확인
        if performance['response_time_ms'] > stage.speed_threshold_ms:
            failed_conditions.append(
                f"응답 속도 느림: {performance['response_time_ms']:.1f}ms > {stage.speed_threshold_ms}ms"
            )
        
        # 메모리 사용량 확인
        if performance['memory_usage_mb'] > stage.memory_threshold_mb:
            failed_conditions.append(
                f"메모리 초과: {performance['memory_usage_mb']:.1f}MB > {stage.memory_threshold_mb}MB"
            )
        
        # 독립도 확인
        if performance['independence'] < stage.independence_threshold:
            failed_conditions.append(
                f"독립도 부족: {performance['independence']:.1f}% < {stage.independence_threshold}%"
            )
        
        return len(failed_conditions) == 0, failed_conditions
    
    def record_achievement(self,
                          stage_name: str,
                          performance: Dict,
                          user_id: str = "anonymous") -> Dict:
        """
        달성 기록 (블록체인 포함)
        
        Returns:
            달성 기록 딕셔너리
        """
        # 이미 달성했는지 확인
        existing = [
            a for a in self.achievements 
            if a.get('stage') == stage_name and a.get('user_id') == user_id
        ]
        if existing:
            return existing[0]
        
        # 달성 조건 확인
        achieved, failed = self.check_stage_requirements(stage_name, performance)
        
        if not achieved:
            return {
                'stage': stage_name,
                'achieved': False,
                'failed_conditions': failed,
            }
        
        # 달성 기록 생성
        stage = GROWTH_STAGES[stage_name]
        achievement = {
            'stage': stage_name,
            'user_id': user_id,
            'achieved': True,
            'achieved_at': datetime.now().isoformat(),
            'performance': performance,
            'reward': {
                'amount': stage.reward_amount,
                'type': stage.reward_type,
            },
            'blockchain_hash': None,
        }
        
        # 블록체인 기록 (선택적)
        if self.blockchain_enabled:
            try:
                # 달성 증명 생성
                proof_data = {
                    'stage': stage_name,
                    'user_id': user_id,
                    'performance': performance,
                    'timestamp': achievement['achieved_at'],
                }
                
                # 블록체인에 기록 (pham_sign_v4 사용)
                # 실제 구현 시 스마트 컨트랙트 호출
                blockchain_hash = self._record_to_blockchain(proof_data)
                achievement['blockchain_hash'] = blockchain_hash
                
            except Exception as e:
                print(f"⚠️ 블록체인 기록 실패: {e}")
        
        # 로컬 저장
        self.achievements.append(achievement)
        self._save_achievements()
        
        return achievement
    
    def _record_to_blockchain(self, proof_data: Dict) -> Optional[str]:
        """
        블록체인에 기록
        
        실제 구현 시 스마트 컨트랙트 호출
        """
        if not HAS_BLOCKCHAIN:
            return None
        
        try:
            # 달성 증명을 블록체인에 기록
            # 실제로는 스마트 컨트랙트를 호출하여 기록
            # 여기서는 해시만 반환 (실제 구현 필요)
            import hashlib
            import json
            
            proof_str = json.dumps(proof_data, sort_keys=True)
            proof_hash = hashlib.sha256(proof_str.encode()).hexdigest()
            
            # TODO: 실제 블록체인 기록
            # contract.record_achievement(proof_hash, proof_data)
            
            return proof_hash
        except Exception as e:
            print(f"⚠️ 블록체인 기록 오류: {e}")
            return None
    
    def get_first_achievers(self, stage_name: str) -> List[Dict]:
        """
        최초 달성자 목록
        
        Returns:
            최초 달성자 목록 (시간순 정렬)
        """
        stage_achievements = [
            a for a in self.achievements 
            if a.get('stage') == stage_name and a.get('achieved', False)
        ]
        
        # 시간순 정렬
        stage_achievements.sort(key=lambda x: x.get('achieved_at', ''))
        
        return stage_achievements
    
    def check_first_achiever(self, stage_name: str, user_id: str) -> bool:
        """
        최초 달성자 여부 확인
        
        Returns:
            최초 달성자이면 True
        """
        first_achievers = self.get_first_achievers(stage_name)
        if not first_achievers:
            return True  # 아직 아무도 달성 안 함
        
        return first_achievers[0].get('user_id') == user_id
    
    def get_rewards(self, stage_name: str, is_first: bool = False) -> Dict:
        """
        보상 정보
        
        최초 달성자는 추가 보상
        """
        if stage_name not in GROWTH_STAGES:
            return {}
        
        stage = GROWTH_STAGES[stage_name]
        base_reward = {
            'amount': stage.reward_amount,
            'type': stage.reward_type,
        }
        
        if is_first:
            # 최초 달성자 추가 보상
            base_reward['first_achiever_bonus'] = stage.reward_amount * 0.5
            base_reward['voting_power'] = 1.0  # 재분배 시스템 결정권
        
        return base_reward


def benchmark_performance(cookie) -> Dict:
    """
    Cookie 성능 벤치마크 측정
    
    Args:
        cookie: CuriousBrain 인스턴스
    
    Returns:
        성능 측정 결과
    """
    import time
    
    # 메모리 사용량 측정 (psutil 없으면 대략적 추정)
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
    except ImportError:
        # psutil 없으면 대략적 추정 (기억 수 기반)
        stats = cookie.get_stats()
        memory_count = 0
        if 'brain' in stats and 'hippo' in stats['brain']:
            memory_count = stats['brain']['hippo'].get('word_count', 0)
        # 대략적 추정: 기억 1개당 0.1MB
        memory_mb = memory_count * 0.1 + 50.0  # 기본 50MB
    
    # 응답 속도 측정
    test_question = "안녕"
    start_time = time.time()
    cookie.think(test_question)
    response_time_ms = (time.time() - start_time) * 1000
    
    # 통계에서 정보 가져오기
    stats = cookie.get_stats()
    memory_count = 0
    independence = 0.0
    
    if 'brain' in stats and 'hippo' in stats['brain']:
        memory_count = stats['brain']['hippo'].get('word_count', 0)
    
    try:
        independence = float(stats.get('independence', '0%').replace('%', ''))
    except:
        independence = 0.0
    
    return {
        'memory_count': memory_count,
        'response_time_ms': response_time_ms,
        'memory_usage_mb': memory_mb,
        'independence': independence,
    }

