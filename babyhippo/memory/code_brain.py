"""
CodeBrain: 코드/문서 분산 저장 + 빠른 검색 + 재조합

핵심:
- 긴 코드 → 청크로 분할 → 분산 저장
- Inverted Index → O(1) 검색
- PageRank → 중요도 관리
- 재조합 → 필요한 부분만 완성

연구소급 기능. 화려함 없이 정확하게.
"""

import sqlite3
import hashlib
import time
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class CodeBrain:
    """
    코드/문서 분산 기억 시스템
    
    저장: 코드 → 청킹 → 분산저장 → 인덱싱 → PageRank
    검색: 쿼리 → 인덱스 O(1) → 정렬 → 재조합
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, db_path: str = None, max_chunks: int = 10000):
        """
        Args:
            db_path: DB 경로 (None이면 ~/.babyhippo/code_brain.db)
            max_chunks: 최대 청크 수
        """
        self.max_chunks = max_chunks
        
        # DB 경로
        if db_path is None:
            db_dir = Path.home() / ".babyhippo"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "code_brain.db")
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        
        # Inverted Index (메모리)
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        
        # PageRank 그래프
        if HAS_NETWORKX:
            self.graph = nx.DiGraph()
        else:
            self.graph = None
        
        # 캐시
        self.rank_cache: Dict[str, float] = {}
        self.rank_cache_valid = False
        
        # 인덱스 로드
        self._load_index()
    
    def _init_db(self):
        """DB 초기화"""
        cursor = self.conn.cursor()
        
        # 청크 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                file_id TEXT NOT NULL,
                chunk_type TEXT,
                name TEXT,
                content TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                created_at REAL,
                last_accessed REAL
            )
        ''')
        
        # 파일 메타데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                total_lines INTEGER,
                chunk_count INTEGER,
                created_at REAL,
                last_modified REAL
            )
        ''')
        
        # 청크 연결 (그래프)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunk_edges (
                from_id TEXT,
                to_id TEXT,
                weight REAL DEFAULT 0.5,
                PRIMARY KEY (from_id, to_id)
            )
        ''')
        
        # 인덱스 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inverted_index (
                keyword TEXT,
                chunk_id TEXT,
                frequency INTEGER DEFAULT 1,
                PRIMARY KEY (keyword, chunk_id)
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunks(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_index_keyword ON inverted_index(keyword)')
        
        self.conn.commit()
    
    def _load_index(self):
        """인덱스 메모리 로드"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT keyword, chunk_id FROM inverted_index')
        
        for keyword, chunk_id in cursor.fetchall():
            self.inverted_index[keyword].add(chunk_id)
        
        # 그래프 로드
        if self.graph:
            cursor.execute('SELECT from_id, to_id, weight FROM chunk_edges')
            for from_id, to_id, weight in cursor.fetchall():
                self.graph.add_edge(from_id, to_id, weight=weight)
    
    # ===== 저장 =====
    
    def store(self, filename: str, content: str, importance: float = 0.5) -> str:
        """
        코드/문서 저장 (분산)
        
        Args:
            filename: 파일명
            content: 전체 내용
            importance: 기본 중요도
        
        Returns:
            file_id
        """
        file_id = self._hash(filename)
        now = time.time()
        
        # 1. 청킹
        chunks = self._chunk_code(content, filename)
        
        # 2. 기존 데이터 삭제 (업데이트)
        self._delete_file(file_id)
        
        # 3. 파일 메타 저장
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO files (id, filename, total_lines, chunk_count, created_at, last_modified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_id, filename, content.count('\n') + 1, len(chunks), now, now))
        
        # 4. 청크 저장 + 인덱싱
        chunk_ids = []
        for chunk in chunks:
            chunk_id = self._hash(f"{file_id}:{chunk['name']}:{chunk['start']}")
            chunk_ids.append(chunk_id)
            
            # 청크 저장
            cursor.execute('''
                INSERT INTO chunks (id, file_id, chunk_type, name, content, 
                                   start_line, end_line, importance, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (chunk_id, file_id, chunk['type'], chunk['name'], chunk['content'],
                  chunk['start'], chunk['end'], importance, now, now))
            
            # 인덱싱
            keywords = self._extract_keywords(chunk['content'], chunk['name'])
            for keyword, freq in keywords.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO inverted_index (keyword, chunk_id, frequency)
                    VALUES (?, ?, ?)
                ''', (keyword, chunk_id, freq))
                self.inverted_index[keyword].add(chunk_id)
            
            # 그래프 노드
            if self.graph:
                self.graph.add_node(chunk_id, file=filename, name=chunk['name'])
        
        # 5. 청크 간 연결 (순차 + 호출 관계)
        self._create_chunk_edges(chunks, chunk_ids)
        
        self.conn.commit()
        self.rank_cache_valid = False
        
        # 6. 용량 관리
        self._manage_capacity()
        
        return file_id
    
    def _chunk_code(self, content: str, filename: str) -> List[Dict]:
        """코드를 의미 단위로 분할"""
        chunks = []
        lines = content.split('\n')
        
        # Python 파일
        if filename.endswith('.py'):
            chunks = self._chunk_python(lines)
        # JavaScript/TypeScript
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            chunks = self._chunk_js(lines)
        # 기타 (라인 기반)
        else:
            chunks = self._chunk_generic(lines)
        
        return chunks
    
    def _chunk_python(self, lines: List[str]) -> List[Dict]:
        """Python 코드 청킹 (함수/클래스 단위)"""
        chunks = []
        current_chunk = []
        current_type = 'module'
        current_name = 'header'
        start_line = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 클래스 시작
            if stripped.startswith('class '):
                if current_chunk:
                    chunks.append({
                        'type': current_type,
                        'name': current_name,
                        'content': '\n'.join(current_chunk),
                        'start': start_line,
                        'end': i - 1
                    })
                match = re.match(r'class\s+(\w+)', stripped)
                current_name = match.group(1) if match else 'class'
                current_type = 'class'
                current_chunk = [line]
                start_line = i
            
            # 함수 시작 (최상위)
            elif stripped.startswith('def ') and not line.startswith(' '):
                if current_chunk:
                    chunks.append({
                        'type': current_type,
                        'name': current_name,
                        'content': '\n'.join(current_chunk),
                        'start': start_line,
                        'end': i - 1
                    })
                match = re.match(r'def\s+(\w+)', stripped)
                current_name = match.group(1) if match else 'function'
                current_type = 'function'
                current_chunk = [line]
                start_line = i
            
            else:
                current_chunk.append(line)
        
        # 마지막 청크
        if current_chunk:
            chunks.append({
                'type': current_type,
                'name': current_name,
                'content': '\n'.join(current_chunk),
                'start': start_line,
                'end': len(lines) - 1
            })
        
        return chunks
    
    def _chunk_js(self, lines: List[str]) -> List[Dict]:
        """JavaScript 코드 청킹"""
        chunks = []
        current_chunk = []
        current_name = 'module'
        start_line = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 함수/클래스 시작
            if re.match(r'^(export\s+)?(function|class|const\s+\w+\s*=)', stripped):
                if current_chunk:
                    chunks.append({
                        'type': 'block',
                        'name': current_name,
                        'content': '\n'.join(current_chunk),
                        'start': start_line,
                        'end': i - 1
                    })
                match = re.search(r'(function|class|const)\s+(\w+)', stripped)
                current_name = match.group(2) if match else 'block'
                current_chunk = [line]
                start_line = i
            else:
                current_chunk.append(line)
        
        if current_chunk:
            chunks.append({
                'type': 'block',
                'name': current_name,
                'content': '\n'.join(current_chunk),
                'start': start_line,
                'end': len(lines) - 1
            })
        
        return chunks
    
    def _chunk_generic(self, lines: List[str], chunk_size: int = 50) -> List[Dict]:
        """일반 텍스트 청킹 (라인 단위)"""
        chunks = []
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunks.append({
                'type': 'block',
                'name': f'block_{i // chunk_size}',
                'content': '\n'.join(chunk_lines),
                'start': i,
                'end': min(i + chunk_size - 1, len(lines) - 1)
            })
        
        return chunks
    
    def _extract_keywords(self, content: str, name: str) -> Dict[str, int]:
        """키워드 추출 (빈도 포함) - 영어 + 한글 지원"""
        keywords = defaultdict(int)
        
        # 이름 추가
        keywords[name.lower()] += 3
        
        # 영어 단어 추출
        eng_words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', content)
        
        # 한글 단어 추출
        kor_words = re.findall(r'[가-힣]+', content)
        
        # 불용어
        stopwords = {'self', 'def', 'class', 'return', 'if', 'else', 'for', 'while',
                     'import', 'from', 'in', 'is', 'not', 'and', 'or', 'the', 'a', 'an',
                     'true', 'false', 'none', 'null', 'this', 'var', 'let', 'const',
                     'function', 'async', 'await',
                     '은', '는', '이', '가', '을', '를', '의', '에', '에서', '로', '으로',
                     '와', '과', '도', '만', '요', '네', '야', '고', '하고', '그', '저', '이런'}
        
        for word in eng_words:
            w = word.lower()
            if len(w) > 2 and w not in stopwords:
                keywords[w] += 1
        
        for word in kor_words:
            if len(word) > 1 and word not in stopwords:
                keywords[word] += 1
        
        return dict(keywords)
    
    def _create_chunk_edges(self, chunks: List[Dict], chunk_ids: List[str]):
        """청크 간 연결 생성"""
        cursor = self.conn.cursor()
        
        for i, chunk_id in enumerate(chunk_ids):
            # 순차 연결
            if i > 0:
                cursor.execute('''
                    INSERT OR REPLACE INTO chunk_edges (from_id, to_id, weight)
                    VALUES (?, ?, ?)
                ''', (chunk_ids[i-1], chunk_id, 0.5))
                
                if self.graph:
                    self.graph.add_edge(chunk_ids[i-1], chunk_id, weight=0.5)
            
            # 호출 관계 (같은 파일 내 함수 호출)
            content = chunks[i]['content']
            for j, other_chunk in enumerate(chunks):
                if i != j and other_chunk['name'] in content:
                    cursor.execute('''
                        INSERT OR REPLACE INTO chunk_edges (from_id, to_id, weight)
                        VALUES (?, ?, ?)
                    ''', (chunk_id, chunk_ids[j], 0.8))
                    
                    if self.graph:
                        self.graph.add_edge(chunk_id, chunk_ids[j], weight=0.8)
    
    # ===== 검색 =====
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        빠른 검색 (Inverted Index + PageRank)
        
        Args:
            query: 검색어
            top_k: 반환할 청크 수
        
        Returns:
            관련 청크 목록
        """
        # 1. 키워드 추출 (영어 + 한글)
        eng_keywords = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]+', query.lower())
        kor_keywords = re.findall(r'[가-힣]+', query)
        keywords = eng_keywords + kor_keywords
        
        if not keywords:
            return []
        
        # 2. Inverted Index 검색 (O(1) per keyword)
        candidate_ids: Dict[str, float] = defaultdict(float)
        
        for keyword in keywords:
            if keyword in self.inverted_index:
                for chunk_id in self.inverted_index[keyword]:
                    candidate_ids[chunk_id] += 1.0
        
        if not candidate_ids:
            return []
        
        # 3. PageRank 점수 추가
        ranks = self._get_pagerank()
        for chunk_id in candidate_ids:
            candidate_ids[chunk_id] += ranks.get(chunk_id, 0.1) * 2
        
        # 4. 상위 K개 선택
        sorted_ids = sorted(candidate_ids.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # 5. 청크 데이터 로드
        results = []
        cursor = self.conn.cursor()
        
        for chunk_id, score in sorted_ids:
            cursor.execute('''
                SELECT id, file_id, chunk_type, name, content, start_line, end_line, importance
                FROM chunks WHERE id = ?
            ''', (chunk_id,))
            row = cursor.fetchone()
            
            if row:
                results.append({
                    'id': row[0],
                    'file_id': row[1],
                    'type': row[2],
                    'name': row[3],
                    'content': row[4],
                    'start_line': row[5],
                    'end_line': row[6],
                    'importance': row[7],
                    'score': score
                })
                
                # 검색된 청크 강화 (Hebbian)
                self.reinforce(chunk_id, boost=0.05)
        
        # 동시 검색된 청크들 연결 강화 (co-activation)
        if len(results) > 1:
            self.reinforce_coactivation([r['id'] for r in results], strength=0.03)
        
        self.conn.commit()
        return results
    
    def recall(self, query: str, max_chars: int = 10000) -> str:
        """
        검색 + 재조합
        
        Args:
            query: 검색어
            max_chars: 최대 문자 수
        
        Returns:
            재조합된 코드/내용
        """
        # 1. 검색
        chunks = self.search(query, top_k=20)
        
        if not chunks:
            return ""
        
        # 2. 재조합 (점수순, 문자 제한)
        result_parts = []
        total_chars = 0
        
        for chunk in chunks:
            content = chunk['content']
            
            if total_chars + len(content) > max_chars:
                # 잘라서 추가
                remaining = max_chars - total_chars
                if remaining > 100:
                    result_parts.append(f"# {chunk['name']} ({chunk['type']})\n{content[:remaining]}...")
                break
            
            result_parts.append(f"# {chunk['name']} ({chunk['type']})\n{content}")
            total_chars += len(content)
        
        return "\n\n".join(result_parts)
    
    def _get_pagerank(self) -> Dict[str, float]:
        """PageRank 계산 (캐싱)"""
        if self.rank_cache_valid:
            return self.rank_cache
        
        if self.graph and self.graph.number_of_nodes() > 0:
            try:
                self.rank_cache = nx.pagerank(self.graph, weight='weight')
            except:
                self.rank_cache = {n: 0.1 for n in self.graph.nodes()}
        else:
            # 그래프 없으면 접근 횟수 기반
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, access_count FROM chunks')
            total = sum(row[1] + 1 for row in cursor.fetchall())
            cursor.execute('SELECT id, access_count FROM chunks')
            self.rank_cache = {row[0]: (row[1] + 1) / total for row in cursor.fetchall()}
        
        self.rank_cache_valid = True
        return self.rank_cache
    
    def reinforce(self, chunk_id: str, boost: float = 0.1):
        """
        청크 강화 (검색 시 호출)
        
        - 접근 횟수 증가
        - 중요도 상승
        - 연결된 청크도 약하게 강화 (Hebbian)
        """
        cursor = self.conn.cursor()
        
        # 직접 강화
        cursor.execute('''
            UPDATE chunks 
            SET access_count = access_count + 1,
                importance = MIN(1.0, importance + ?),
                last_accessed = ?
            WHERE id = ?
        ''', (boost, time.time(), chunk_id))
        
        # 연결된 청크도 약하게 강화 (Hebbian spreading)
        if self.graph and chunk_id in self.graph:
            for neighbor in self.graph.neighbors(chunk_id):
                edge_weight = self.graph[chunk_id][neighbor].get('weight', 0.5)
                neighbor_boost = boost * edge_weight * 0.3  # 30% 전파
                cursor.execute('''
                    UPDATE chunks 
                    SET importance = MIN(1.0, importance + ?)
                    WHERE id = ?
                ''', (neighbor_boost, neighbor))
                
                # 그래프 엣지 강화
                self.graph[chunk_id][neighbor]['weight'] = min(1.0, edge_weight + 0.05)
        
        self.conn.commit()
        self.rank_cache_valid = False  # PageRank 재계산 필요
    
    def reinforce_coactivation(self, chunk_ids: List[str], strength: float = 0.1):
        """
        동시 활성화된 청크들 연결 강화 (Hebbian)
        
        "같이 검색되면 연결이 강해진다"
        """
        if not self.graph or len(chunk_ids) < 2:
            return
        
        cursor = self.conn.cursor()
        
        for i, id1 in enumerate(chunk_ids):
            for id2 in chunk_ids[i+1:]:
                if self.graph.has_edge(id1, id2):
                    # 기존 연결 강화
                    w = self.graph[id1][id2].get('weight', 0.5)
                    new_w = min(1.0, w + strength)
                    self.graph[id1][id2]['weight'] = new_w
                    self.graph[id2][id1]['weight'] = new_w
                else:
                    # 새 연결 생성
                    self.graph.add_edge(id1, id2, weight=strength)
                    self.graph.add_edge(id2, id1, weight=strength)
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO chunk_edges (from_id, to_id, weight)
                        VALUES (?, ?, ?)
                    ''', (id1, id2, strength))
        
        self.conn.commit()
        self.rank_cache_valid = False
    
    # ===== 관리 =====
    
    def _manage_capacity(self):
        """용량 관리 - 오래되고 덜 중요한 청크 삭제"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chunks')
        count = cursor.fetchone()[0]
        
        if count <= self.max_chunks:
            return
        
        # 삭제할 개수
        to_delete = count - int(self.max_chunks * 0.8)
        
        # 점수 낮은 순 삭제 (중요도 * 0.3 + 접근 * 0.3 + 최근성 * 0.4)
        cursor.execute('''
            SELECT id FROM chunks
            ORDER BY (importance * 0.3 + 
                      MIN(access_count, 10) / 10.0 * 0.3 + 
                      (last_accessed - ?) / 86400.0 * 0.4)
            ASC LIMIT ?
        ''', (time.time(), to_delete))
        
        ids_to_delete = [row[0] for row in cursor.fetchall()]
        
        for chunk_id in ids_to_delete:
            self._delete_chunk(chunk_id)
        
        self.conn.commit()
    
    def _delete_chunk(self, chunk_id: str):
        """청크 삭제"""
        cursor = self.conn.cursor()
        
        # 인덱스에서 제거
        cursor.execute('SELECT keyword FROM inverted_index WHERE chunk_id = ?', (chunk_id,))
        for row in cursor.fetchall():
            self.inverted_index[row[0]].discard(chunk_id)
        
        cursor.execute('DELETE FROM inverted_index WHERE chunk_id = ?', (chunk_id,))
        cursor.execute('DELETE FROM chunk_edges WHERE from_id = ? OR to_id = ?', (chunk_id, chunk_id))
        cursor.execute('DELETE FROM chunks WHERE id = ?', (chunk_id,))
        
        if self.graph and chunk_id in self.graph:
            self.graph.remove_node(chunk_id)
        
        self.rank_cache_valid = False
    
    def _delete_file(self, file_id: str):
        """파일의 모든 청크 삭제"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM chunks WHERE file_id = ?', (file_id,))
        
        for row in cursor.fetchall():
            self._delete_chunk(row[0])
        
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
    
    def _hash(self, content: str) -> str:
        """해시 생성"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    # ===== 통계 =====
    
    def reindex_all(self):
        """모든 청크 재인덱싱 (키워드 추출 방식 변경 시)"""
        cursor = self.conn.cursor()
        
        # 기존 인덱스 삭제
        cursor.execute('DELETE FROM inverted_index')
        self.inverted_index.clear()
        
        # 모든 청크 재인덱싱
        cursor.execute('SELECT id, name, content FROM chunks')
        for chunk_id, name, content in cursor.fetchall():
            keywords = self._extract_keywords(content, name)
            for keyword, freq in keywords.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO inverted_index (keyword, chunk_id, frequency)
                    VALUES (?, ?, ?)
                ''', (keyword, chunk_id, freq))
                self.inverted_index[keyword].add(chunk_id)
        
        self.conn.commit()
        self.rank_cache_valid = False
        return len(self.inverted_index)
    
    def get_stats(self) -> Dict:
        """통계"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM files')
        file_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chunks')
        chunk_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT keyword) FROM inverted_index')
        keyword_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM chunk_edges')
        edge_count = cursor.fetchone()[0]
        
        return {
            'version': self.VERSION,
            'files': file_count,
            'chunks': chunk_count,
            'max_chunks': self.max_chunks,
            'keywords': keyword_count,
            'edges': edge_count,
            'db_path': self.db_path
        }
    
    def get_files(self) -> List[Dict]:
        """저장된 파일 목록"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, filename, total_lines, chunk_count, created_at, last_modified
            FROM files ORDER BY last_modified DESC
        ''')
        
        return [{
            'id': row[0],
            'filename': row[1],
            'lines': row[2],
            'chunks': row[3],
            'created': row[4],
            'modified': row[5]
        } for row in cursor.fetchall()]
    
    def close(self):
        """연결 종료"""
        self.conn.close()


# ===== 편의 함수 =====

def create_code_brain(max_chunks: int = 10000) -> CodeBrain:
    """CodeBrain 인스턴스 생성"""
    return CodeBrain(max_chunks=max_chunks)

