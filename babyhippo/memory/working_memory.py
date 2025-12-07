"""
PersistentWorkingMemory: 영구 작업 기억

세션 종료, 재부팅, 한 달 후에도 작업 내용을 기억합니다.

주요 기능:
- 코드/문서 전체 저장 (요약 아닌 원본)
- 최대 N개 슬롯 (기본 3개)
- LRU + 중요도 기반 자동 교체
- SQLite 영구 저장
- 세션 시작 시 자동 복원

사용법:
    memory = PersistentWorkingMemory()
    
    # 코드 저장
    memory.save_work("brain_graph.py", code_content, work_type="code")
    
    # 복원 (자동)
    recent_works = memory.get_recent_works()
    
    # AI 컨텍스트용
    context = memory.get_context_for_ai()
"""

import sqlite3
import time
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class PersistentWorkingMemory:
    """
    영구 작업 기억
    
    특징:
    - 코드/문서 전체 저장 (최대 100KB per slot)
    - 슬롯 기반 관리 (기본 3개)
    - 중요도 + 최근성 기반 교체
    - SQLite 영구 저장
    """
    
    VERSION = "1.0.0"
    
    def __init__(
        self,
        db_path: str = None,
        max_slots: int = 3,
        max_size_per_slot: int = 100000,  # 100KB (약 2000줄)
    ):
        """
        초기화
        
        Args:
            db_path: DB 파일 경로 (None이면 기본 경로)
            max_slots: 최대 슬롯 수
            max_size_per_slot: 슬롯당 최대 크기 (bytes)
        """
        self.max_slots = max_slots
        self.max_size = max_size_per_slot
        
        # DB 경로 설정
        if db_path is None:
            db_dir = Path.home() / ".babyhippo"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "working_memory.db")
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        
        # 통계
        self.total_saves = 0
        self.total_restores = 0
    
    def _init_db(self):
        """데이터베이스 초기화"""
        cursor = self.conn.cursor()
        
        # 작업 슬롯 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_slots (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                work_type TEXT DEFAULT 'code',
                summary TEXT,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                metadata TEXT
            )
        ''')
        
        # 작업 히스토리 (삭제된 작업도 요약 보관)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_history (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                summary TEXT,
                work_type TEXT,
                created_at REAL,
                deleted_at REAL,
                total_accesses INTEGER
            )
        ''')
        
        # 세션 로그 (언제 작업했는지)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at REAL NOT NULL,
                ended_at REAL,
                works_accessed TEXT
            )
        ''')
        
        self.conn.commit()
    
    def save_work(
        self,
        name: str,
        content: str,
        work_type: str = "code",
        importance: float = 0.5,
        metadata: Dict = None
    ) -> str:
        """
        작업 저장
        
        Args:
            name: 작업 이름 (예: "brain_graph.py")
            content: 전체 내용
            work_type: 작업 유형 (code, document, notes)
            importance: 중요도 (0.0 ~ 1.0)
            metadata: 추가 메타데이터
        
        Returns:
            work_id: 저장된 작업 ID
        """
        # 크기 제한
        if len(content) > self.max_size:
            content = content[:self.max_size]
            # 마지막 완전한 줄까지만
            last_newline = content.rfind('\n')
            if last_newline > 0:
                content = content[:last_newline]
        
        # ID 생성 (이름 기반 - 같은 파일은 업데이트)
        work_id = self._generate_id(name)
        
        # 요약 생성
        summary = self._generate_summary(name, content, work_type)
        
        now = time.time()
        
        cursor = self.conn.cursor()
        
        # 이미 존재하면 업데이트
        cursor.execute('SELECT id, access_count FROM work_slots WHERE id = ?', (work_id,))
        existing = cursor.fetchone()
        
        if existing:
            # 업데이트
            access_count = existing[1] + 1
            cursor.execute('''
                UPDATE work_slots 
                SET content = ?, summary = ?, importance = ?, 
                    access_count = ?, last_accessed = ?, metadata = ?
                WHERE id = ?
            ''', (content, summary, importance, access_count, now,
                  json.dumps(metadata or {}), work_id))
        else:
            # 슬롯 확인
            cursor.execute('SELECT COUNT(*) FROM work_slots')
            count = cursor.fetchone()[0]
            
            if count >= self.max_slots:
                # 가장 오래되고 덜 중요한 것 제거
                self._evict_oldest()
            
            # 새로 저장
            cursor.execute('''
                INSERT INTO work_slots 
                (id, name, content, work_type, summary, importance, 
                 access_count, created_at, last_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (work_id, name, content, work_type, summary, importance,
                  1, now, now, json.dumps(metadata or {})))
        
        self.conn.commit()
        self.total_saves += 1
        
        return work_id
    
    def get_work(self, name: str) -> Optional[Dict]:
        """특정 작업 조회"""
        work_id = self._generate_id(name)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, content, work_type, summary, importance,
                   access_count, created_at, last_accessed, metadata
            FROM work_slots WHERE id = ?
        ''', (work_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        # 접근 기록 업데이트
        cursor.execute('''
            UPDATE work_slots 
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        ''', (time.time(), work_id))
        self.conn.commit()
        
        return {
            'id': row[0],
            'name': row[1],
            'content': row[2],
            'work_type': row[3],
            'summary': row[4],
            'importance': row[5],
            'access_count': row[6],
            'created_at': row[7],
            'last_accessed': row[8],
            'metadata': json.loads(row[9]) if row[9] else {}
        }
    
    def get_recent_works(self, limit: int = None) -> List[Dict]:
        """최근 작업 목록 조회"""
        if limit is None:
            limit = self.max_slots
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, content, work_type, summary, importance,
                   access_count, created_at, last_accessed, metadata
            FROM work_slots 
            ORDER BY last_accessed DESC
            LIMIT ?
        ''', (limit,))
        
        works = []
        for row in cursor.fetchall():
            works.append({
                'id': row[0],
                'name': row[1],
                'content': row[2],
                'work_type': row[3],
                'summary': row[4],
                'importance': row[5],
                'access_count': row[6],
                'created_at': row[7],
                'last_accessed': row[8],
                'metadata': json.loads(row[9]) if row[9] else {}
            })
        
        self.total_restores += 1
        return works
    
    def get_context_for_ai(self, max_chars: int = 50000) -> str:
        """
        AI에게 전달할 작업 컨텍스트 생성
        
        Returns:
            AI가 참고할 작업 기억 문자열
        """
        works = self.get_recent_works()
        
        if not works:
            return ""
        
        context_parts = ["[📁 작업 기억 - 이전 세션에서 작업한 내용]\n"]
        total_chars = 0
        
        for i, work in enumerate(works, 1):
            # 시간 포맷
            last_time = datetime.fromtimestamp(work['last_accessed'])
            time_str = last_time.strftime("%Y-%m-%d %H:%M")
            
            # 헤더
            header = f"\n### {i}. {work['name']} ({work['work_type']})\n"
            header += f"마지막 작업: {time_str} | 접근: {work['access_count']}회\n"
            header += f"요약: {work['summary']}\n"
            header += "```\n"
            
            # 내용 (남은 공간만큼)
            remaining = max_chars - total_chars - len(header) - 100
            if remaining <= 0:
                break
            
            content = work['content']
            if len(content) > remaining:
                content = content[:remaining] + "\n... (truncated)"
            
            footer = "\n```\n"
            
            part = header + content + footer
            context_parts.append(part)
            total_chars += len(part)
        
        return "".join(context_parts)
    
    def get_summary_context(self) -> str:
        """요약만 포함한 컨텍스트 (가벼운 버전)"""
        works = self.get_recent_works()
        
        if not works:
            return ""
        
        lines = ["[📁 최근 작업 요약]"]
        for work in works:
            last_time = datetime.fromtimestamp(work['last_accessed'])
            time_str = last_time.strftime("%m/%d %H:%M")
            lines.append(f"- {work['name']}: {work['summary']} ({time_str})")
        
        return "\n".join(lines)
    
    def delete_work(self, name: str) -> bool:
        """작업 삭제 (히스토리에 요약 보관)"""
        work_id = self._generate_id(name)
        
        cursor = self.conn.cursor()
        
        # 기존 데이터 조회
        cursor.execute('''
            SELECT name, summary, work_type, created_at, access_count
            FROM work_slots WHERE id = ?
        ''', (work_id,))
        row = cursor.fetchone()
        
        if not row:
            return False
        
        # 히스토리에 보관
        cursor.execute('''
            INSERT OR REPLACE INTO work_history
            (id, name, summary, work_type, created_at, deleted_at, total_accesses)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (work_id, row[0], row[1], row[2], row[3], time.time(), row[4]))
        
        # 슬롯에서 삭제
        cursor.execute('DELETE FROM work_slots WHERE id = ?', (work_id,))
        
        self.conn.commit()
        return True
    
    def clear_all(self):
        """모든 작업 삭제 (주의!)"""
        cursor = self.conn.cursor()
        
        # 히스토리에 백업
        cursor.execute('''
            INSERT INTO work_history 
            (id, name, summary, work_type, created_at, deleted_at, total_accesses)
            SELECT id, name, summary, work_type, created_at, ?, access_count
            FROM work_slots
        ''', (time.time(),))
        
        cursor.execute('DELETE FROM work_slots')
        self.conn.commit()
    
    def get_stats(self) -> Dict:
        """통계 조회"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM work_slots')
        slot_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(LENGTH(content)) FROM work_slots')
        total_size = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM work_history')
        history_count = cursor.fetchone()[0]
        
        return {
            'version': self.VERSION,
            'db_path': self.db_path,
            'max_slots': self.max_slots,
            'used_slots': slot_count,
            'total_size_bytes': total_size,
            'total_size_kb': round(total_size / 1024, 2),
            'history_count': history_count,
            'total_saves': self.total_saves,
            'total_restores': self.total_restores,
        }
    
    def log_session_start(self):
        """세션 시작 로그"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO session_log (started_at) VALUES (?)
        ''', (time.time(),))
        self.conn.commit()
        return cursor.lastrowid
    
    def log_session_end(self, session_id: int, works_accessed: List[str]):
        """세션 종료 로그"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE session_log 
            SET ended_at = ?, works_accessed = ?
            WHERE id = ?
        ''', (time.time(), json.dumps(works_accessed), session_id))
        self.conn.commit()
    
    # ===== Private Methods =====
    
    def _generate_id(self, name: str) -> str:
        """이름 기반 ID 생성 (같은 파일은 같은 ID)"""
        return hashlib.md5(name.lower().encode()).hexdigest()[:12]
    
    def _generate_summary(self, name: str, content: str, work_type: str) -> str:
        """작업 요약 생성"""
        lines = content.split('\n')
        line_count = len(lines)
        
        # 코드 타입별 요약
        if work_type == 'code':
            # 클래스/함수 찾기
            classes = [l.strip() for l in lines if l.strip().startswith('class ')]
            functions = [l.strip() for l in lines if l.strip().startswith('def ')]
            
            summary_parts = [f"{line_count}줄"]
            if classes:
                summary_parts.append(f"클래스 {len(classes)}개")
            if functions:
                summary_parts.append(f"함수 {len(functions)}개")
            
            return f"{name} - " + ", ".join(summary_parts)
        
        else:
            # 문서
            char_count = len(content)
            return f"{name} - {line_count}줄, {char_count}자"
    
    def _evict_oldest(self):
        """가장 오래되고 덜 중요한 작업 제거"""
        cursor = self.conn.cursor()
        
        # 점수 계산: importance * 0.3 + recency * 0.4 + access * 0.3
        cursor.execute('''
            SELECT id, name, summary, work_type, created_at, access_count,
                   importance, last_accessed
            FROM work_slots
            ORDER BY 
                (importance * 0.3 + 
                 (last_accessed - ?) / 86400.0 * 0.4 + 
                 MIN(access_count, 10) / 10.0 * 0.3)
            ASC
            LIMIT 1
        ''', (time.time(),))
        
        row = cursor.fetchone()
        if row:
            work_id = row[0]
            
            # 히스토리에 보관
            cursor.execute('''
                INSERT OR REPLACE INTO work_history
                (id, name, summary, work_type, created_at, deleted_at, total_accesses)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (work_id, row[1], row[2], row[3], row[4], time.time(), row[5]))
            
            # 삭제
            cursor.execute('DELETE FROM work_slots WHERE id = ?', (work_id,))
            self.conn.commit()
    
    def close(self):
        """연결 종료"""
        self.conn.close()


# ===== 편의 함수 =====

def create_working_memory(max_slots: int = 3) -> PersistentWorkingMemory:
    """작업 기억 인스턴스 생성"""
    return PersistentWorkingMemory(max_slots=max_slots)


# ===== 코드 감지 유틸 =====

def detect_code_in_message(message: str) -> Optional[Dict]:
    """
    메시지에서 코드 감지
    
    Returns:
        {'name': 파일명, 'content': 코드, 'type': 'code'} or None
    """
    # 코드 블록 패턴
    import re
    
    # ```python ... ``` 형식
    code_block = re.search(r'```(\w+)?\n(.*?)```', message, re.DOTALL)
    if code_block:
        lang = code_block.group(1) or 'code'
        code = code_block.group(2).strip()
        if len(code) > 100:  # 최소 100자 이상
            return {
                'name': f'code_snippet.{lang}',
                'content': code,
                'type': 'code'
            }
    
    # 파일 내용처럼 보이는 경우 (class, def, import 등)
    if len(message) > 200:
        code_indicators = ['class ', 'def ', 'import ', 'from ', 'function ', 'const ', 'let ', 'var ']
        indicator_count = sum(1 for ind in code_indicators if ind in message)
        
        if indicator_count >= 2:
            # 파일명 추출 시도
            filename_match = re.search(r'(\w+\.py|\w+\.js|\w+\.ts)', message)
            filename = filename_match.group(1) if filename_match else 'detected_code.txt'
            
            return {
                'name': filename,
                'content': message,
                'type': 'code'
            }
    
    return None

