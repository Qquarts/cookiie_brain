"""
CoreMemory: AI의 핵심 기억 (성격/지식/가치관)

- 중요한 정보 완전 저장
- 모든 대화에서 항상 적용
- AI의 "성격"처럼 작동

저장 방식:
1. 사용자 요청: "이거 기억해", "저장해"
2. AI 자동 판단: 중요한 개념 감지 시

적용 방식:
- 모든 대화의 시스템 프롬프트에 포함
- AI가 항상 염두에 두고 응답
"""

import sqlite3
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class CoreMemory:
    """
    AI의 핵심 기억
    
    - 사용자 정보 (이름, 직업, 선호)
    - 프로젝트 정보 (현재 작업, 목표)
    - 중요 개념 (기술, 원칙)
    - 지시사항 (AI 행동 방식)
    """
    
    VERSION = "1.0.0"
    
    # 메모리 카테고리
    CATEGORIES = {
        'user': '사용자 정보',
        'project': '프로젝트/작업',
        'concept': '중요 개념',
        'preference': '선호/스타일',
        'instruction': '지시사항',
        'fact': '사실/정보',
    }
    
    def __init__(self, db_path: str = None, max_memories: int = 100):
        """
        Args:
            db_path: DB 경로
            max_memories: 최대 메모리 수
        """
        self.max_memories = max_memories
        
        if db_path is None:
            db_dir = Path.home() / ".babyhippo"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "core_memory.db")
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self._init_default_personality()
    
    def _init_db(self):
        """DB 초기화"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT DEFAULT 'user',
                importance REAL DEFAULT 0.8,
                created_at REAL,
                updated_at REAL,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # 변경 이력
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER,
                action TEXT,
                old_content TEXT,
                new_content TEXT,
                timestamp REAL
            )
        ''')
        
        self.conn.commit()
    
    def _init_default_personality(self):
        """기본 성격 초기화 (최초 1회만)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories WHERE category = 'instruction'")
        if cursor.fetchone()[0] == 0:
            # 기본 성격이 없으면 추가
            defaults = [
                ("사용자 요청을 우선 수행. 먼저 맞춰주고, 안정성 확인 후 확장", "instruction"),
                ("질문은 중요한 순간에만. 막 질문하면 파급력이 떨어짐", "instruction"),
                ("대화가 쌓일수록 점점 더 능동적으로 변화", "instruction"),
            ]
            for content, category in defaults:
                self.add(content, category=category, source='system', importance=1.0)
    
    def add(self, content: str, category: str = 'fact', 
            source: str = 'user', importance: float = 0.8) -> int:
        """
        핵심 메모리 추가
        
        Args:
            content: 기억 내용
            category: 카테고리 (user, project, concept, preference, instruction, fact)
            source: 출처 (user=사용자 요청, auto=AI 자동)
            importance: 중요도
        
        Returns:
            memory_id
        """
        now = time.time()
        cursor = self.conn.cursor()
        
        # 중복 체크 (유사한 내용 있으면 업데이트)
        cursor.execute('''
            SELECT id, content FROM memories 
            WHERE category = ? AND content LIKE ?
        ''', (category, f'%{content[:50]}%'))
        
        existing = cursor.fetchone()
        if existing:
            # 업데이트
            return self.update(existing[0], content)
        
        # 새로 추가
        cursor.execute('''
            INSERT INTO memories (category, content, source, importance, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, content, source, importance, now, now))
        
        memory_id = cursor.lastrowid
        
        # 이력 저장
        cursor.execute('''
            INSERT INTO memory_history (memory_id, action, new_content, timestamp)
            VALUES (?, 'add', ?, ?)
        ''', (memory_id, content, now))
        
        self.conn.commit()
        
        # 용량 관리
        self._manage_capacity()
        
        return memory_id
    
    def update(self, memory_id: int, new_content: str) -> int:
        """메모리 업데이트"""
        cursor = self.conn.cursor()
        now = time.time()
        
        # 기존 내용 조회
        cursor.execute('SELECT content FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        old_content = row[0] if row else None
        
        # 업데이트
        cursor.execute('''
            UPDATE memories SET content = ?, updated_at = ?, access_count = access_count + 1
            WHERE id = ?
        ''', (new_content, now, memory_id))
        
        # 이력 저장
        cursor.execute('''
            INSERT INTO memory_history (memory_id, action, old_content, new_content, timestamp)
            VALUES (?, 'update', ?, ?, ?)
        ''', (memory_id, old_content, new_content, now))
        
        self.conn.commit()
        return memory_id
    
    def delete(self, memory_id: int) -> bool:
        """메모리 삭제"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT content FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        # 이력 저장
        cursor.execute('''
            INSERT INTO memory_history (memory_id, action, old_content, timestamp)
            VALUES (?, 'delete', ?, ?)
        ''', (memory_id, row[0], time.time()))
        
        cursor.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
        self.conn.commit()
        return True
    
    def get_all(self) -> List[Dict]:
        """모든 메모리 조회"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, category, content, source, importance, created_at, updated_at, access_count
            FROM memories ORDER BY importance DESC, updated_at DESC
        ''')
        
        return [{
            'id': row[0],
            'category': row[1],
            'content': row[2],
            'source': row[3],
            'importance': row[4],
            'created_at': row[5],
            'updated_at': row[6],
            'access_count': row[7]
        } for row in cursor.fetchall()]
    
    def reinforce(self, memory_id: int, boost: float = 0.05):
        """
        기억 강화 (반복 검색 시 호출)
        
        - 접근 횟수 증가
        - 중요도 상승 (최대 1.0)
        - Hebbian 원리: 자주 쓰이면 강해짐
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET access_count = access_count + 1,
                importance = MIN(1.0, importance + ?),
                updated_at = ?
            WHERE id = ?
        ''', (boost, time.time(), memory_id))
        self.conn.commit()
    
    def reinforce_by_content(self, keyword: str, boost: float = 0.03):
        """키워드 포함된 기억 강화"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET access_count = access_count + 1,
                importance = MIN(1.0, importance + ?)
            WHERE content LIKE ?
        ''', (boost, f'%{keyword}%'))
        self.conn.commit()
    
    def decay_all(self, rate: float = 0.01):
        """
        전체 기억 감쇠 (시간 지나면 약해짐)
        
        - 중요도 낮은 것은 더 빨리 감쇠
        - 최소값 0.1 유지
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET importance = MAX(0.1, importance - ? * (1.1 - importance))
        ''', (rate,))
        self.conn.commit()
    
    def get_by_category(self, category: str) -> List[Dict]:
        """카테고리별 조회"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, category, content, source, importance, updated_at
            FROM memories WHERE category = ?
            ORDER BY importance DESC
        ''', (category,))
        
        return [{
            'id': row[0],
            'category': row[1],
            'content': row[2],
            'source': row[3],
            'importance': row[4],
            'updated_at': row[5]
        } for row in cursor.fetchall()]
    
    def get_context_for_ai(self) -> str:
        """
        AI 시스템 프롬프트용 컨텍스트 생성
        
        모든 대화에서 AI가 참고할 핵심 정보
        """
        memories = self.get_all()
        
        if not memories:
            return ""
        
        lines = ["[🧠 핵심 기억 - 항상 염두에 두세요]"]
        
        # 카테고리별 정리
        by_category = {}
        for mem in memories:
            cat = mem['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(mem['content'])
        
        # 출력
        for cat, contents in by_category.items():
            cat_name = self.CATEGORIES.get(cat, cat)
            lines.append(f"\n**{cat_name}:**")
            for content in contents:
                lines.append(f"• {content}")
        
        return "\n".join(lines)
    
    def get_summary(self) -> str:
        """간단 요약"""
        memories = self.get_all()
        if not memories:
            return "핵심 기억 없음"
        
        return " | ".join([m['content'][:30] + "..." for m in memories[:5]])
    
    def _manage_capacity(self):
        """용량 관리"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        count = cursor.fetchone()[0]
        
        if count <= self.max_memories:
            return
        
        # 중요도 낮고 오래된 것 삭제
        to_delete = count - int(self.max_memories * 0.8)
        cursor.execute('''
            SELECT id FROM memories
            ORDER BY importance ASC, updated_at ASC
            LIMIT ?
        ''', (to_delete,))
        
        for row in cursor.fetchall():
            self.delete(row[0])
    
    def get_stats(self) -> Dict:
        """통계"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM memories')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT category, COUNT(*) FROM memories GROUP BY category')
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'version': self.VERSION,
            'total': total,
            'max': self.max_memories,
            'by_category': by_category,
            'db_path': self.db_path
        }
    
    def close(self):
        self.conn.close()


# ===== 메모리 요청 감지 =====

def detect_memory_request(message: str) -> Optional[Dict]:
    """
    메모리 저장 요청 감지
    
    Returns:
        {'action': 'save'/'update'/'delete', 'content': ..., 'category': ...}
    """
    message_lower = message.lower()
    
    # 저장 요청 패턴
    save_patterns = [
        '기억해', '저장해', '메모해', '기억 해', '저장 해',
        'remember', 'save', 'memo',
        '잊지마', '잊지 마', '명심해',
        '중요해', '중요한 거야', '핵심이야',
    ]
    
    # 삭제 요청 패턴
    delete_patterns = [
        '잊어', '삭제해', '지워', '잊어버려',
        'forget', 'delete', 'remove',
    ]
    
    for pattern in save_patterns:
        if pattern in message_lower:
            # 카테고리 추론
            category = 'fact'
            if any(w in message_lower for w in ['내 이름', '나는', '저는', '내가']):
                category = 'user'
            elif any(w in message_lower for w in ['프로젝트', '작업', '개발', '만들']):
                category = 'project'
            elif any(w in message_lower for w in ['좋아', '싫어', '선호', '스타일']):
                category = 'preference'
            elif any(w in message_lower for w in ['항상', '언제나', '규칙', '지시']):
                category = 'instruction'
            elif any(w in message_lower for w in ['개념', '원리', '기술', '방법']):
                category = 'concept'
            
            return {
                'action': 'save',
                'content': message,  # AI가 요약해서 저장
                'category': category
            }
    
    for pattern in delete_patterns:
        if pattern in message_lower:
            return {
                'action': 'delete',
                'content': message,
                'category': None
            }
    
    return None


def detect_important_concept(message: str, response: str) -> Optional[str]:
    """
    AI가 자동으로 중요 개념 감지
    
    대화 내용에서 저장할 만한 중요 정보 추출
    """
    # 중요 정보 패턴
    important_patterns = [
        r'내 이름은\s+(\S+)',
        r'나는\s+(\S+)이야',
        r'(\d{4})년생',
        r'직업은?\s+(\S+)',
        r'(\S+)\s*프로젝트',
    ]
    
    import re
    for pattern in important_patterns:
        match = re.search(pattern, message)
        if match:
            return match.group(0)
    
    return None

