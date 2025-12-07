"""
babyHippo Pro: Conversation Memory System
3-Tier memory architecture for real dialogue storage

Author: GNJz (Qquarts)
Version: Pro 1.0
"""
import json
import sqlite3
from datetime import datetime
from collections import deque

# 모듈 임포트 (새 구조)
from .hippo_memory import HippoMemory


class ConversationMemory:
    """
    3-Tier Memory System for Real Conversations
    
    Tier 1 (Working): babyHippo - Last 100 exchanges (~1 MB)
    Tier 2 (Episodic): SQLite - Last month (~20 MB)
    Tier 3 (Semantic): JSON Archive - Full history (~200 MB/year)
    """
    
    def __init__(self, db_path="conversations.db", archive_path="archive.json"):
        # Tier 1: Working memory (babyHippo)
        self.hippo = HippoMemory()
        self.working_memory = deque(maxlen=100)  # Last 100 exchanges
        
        # Tier 2: Episodic memory (SQLite)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)  # Gradio 멀티스레드 지원
        self._init_db()
        
        # Tier 3: Semantic memory (Archive)
        self.archive_path = archive_path
        
        # Metadata
        self.conversation_id = self._get_next_id()
    
    def _init_db(self):
        """Initialize SQLite database for episodic memory"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user_msg TEXT,
                ai_response TEXT,
                context TEXT,
                keywords TEXT,
                importance REAL
            )
        """)
        self.conn.commit()
    
    def _get_next_id(self):
        """Get the next available conversation ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(id) FROM conversations")
        result = cursor.fetchone()[0]
        return (result + 1) if result is not None else 0
    
    def learn(self, user_msg, ai_response=None, context="general"):
        """
        Store a conversation exchange
        
        Args:
            user_msg: User's message
            ai_response: AI's response (optional)
            context: Conversation context
        """
        timestamp = datetime.now().isoformat()
        
        # Extract keywords from both user message and AI response
        keywords = self._extract_keywords(user_msg)
        
        # If AI response has important info, add those keywords too
        if ai_response:
            response_keywords = self._extract_keywords(ai_response)
            # Merge keywords (avoid duplicates)
            all_keywords = list(dict.fromkeys(keywords + response_keywords))[:8]
        else:
            all_keywords = keywords
        
        # Compute importance based on both user message and response
        user_importance = self._compute_importance(user_msg, keywords)
        response_importance = self._compute_importance(ai_response, response_keywords) if ai_response else 0.0
        
        # Final importance: max of both (answers with facts are more important)
        importance = max(user_importance, response_importance)
        
        # Tier 1: Store in working memory (babyHippo)
        conv_id = f"conv_{self.conversation_id}"
        self.working_memory.append({
            'id': conv_id,
            'timestamp': timestamp,
            'user_msg': user_msg,
            'ai_response': ai_response,
            'context': context,
            'keywords': keywords
        })
        
        # Store keywords in babyHippo for fast recall
        for kw in all_keywords[:5]:  # Top 5 keywords (including response keywords)
            self.hippo.learn(f"{kw}_{conv_id}", context=context)
        
        # Tier 2: Store in episodic memory (SQLite)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations 
            (id, timestamp, user_msg, ai_response, context, keywords, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.conversation_id,
            timestamp,
            user_msg,
            ai_response,
            context,
            ",".join(all_keywords),
            importance
        ))
        self.conn.commit()
        
        # Sleep consolidation for important memories
        if importance > 0.7:
            self.hippo.sleep(cycles=5)
        
        self.conversation_id += 1
        
        return conv_id
    
    def recall(self, query, max_results=5, min_importance=0.0):
        """
        Recall conversations related to query
        
        Args:
            query: Search query
            max_results: Maximum number of results
            min_importance: Minimum importance threshold
        
        Returns:
            List of conversation records
        """
        # Step 1: Fast keyword search in babyHippo
        keywords = self._extract_keywords(query)
        related_conv_ids = []
        
        for kw in keywords:
            results = self.hippo.recall(kw, top_n=3)
            if isinstance(results, list):
                related_conv_ids.extend([r[0].split('_')[-1] for r in results])
            elif results:
                related_conv_ids.append(results.split('_')[-1])
        
        # Step 2: Retrieve from SQLite
        cursor = self.conn.cursor()
        
        if related_conv_ids:
            # Use babyHippo results
            placeholders = ','.join('?' * len(related_conv_ids))
            cursor.execute(f"""
                SELECT id, timestamp, user_msg, ai_response, context, keywords, importance
                FROM conversations
                WHERE id IN ({placeholders}) AND importance >= ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            """, (*related_conv_ids, min_importance, max_results))
        else:
            # Fallback: keyword-based search in SQLite
            # Extract keywords from query and search for ANY of them
            query_keywords = self._extract_keywords(query)
            
            # Build OR conditions for each keyword
            conditions = []
            params = []
            for kw in query_keywords[:5]:  # Use top 5 keywords
                search_term = f"%{kw}%"
                conditions.append("(user_msg LIKE ? OR ai_response LIKE ? OR keywords LIKE ?)")
                params.extend([search_term, search_term, search_term])
            
            if conditions:
                where_clause = " OR ".join(conditions)
                params.append(min_importance)
                params.append(max_results)
                
                cursor.execute(f"""
                    SELECT id, timestamp, user_msg, ai_response, context, keywords, importance
                    FROM conversations
                    WHERE ({where_clause}) AND importance >= ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                """, tuple(params))
            else:
                # No keywords, return empty
                cursor.execute("SELECT * FROM conversations WHERE 0")
        
        results = cursor.fetchall()
        
        return [
            {
                'id': r[0],
                'timestamp': r[1],
                'user_msg': r[2],
                'ai_response': r[3],
                'context': r[4],
                'keywords': r[5].split(','),
                'importance': r[6]
            }
            for r in results
        ]
    
    def get_recent(self, n=10):
        """Get n most recent conversations"""
        return list(self.working_memory)[-n:]
    
    def get_stats(self):
        """Get memory statistics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        hippo_stats = self.hippo.get_stats()
        
        return {
            'working_memory': len(self.working_memory),
            'episodic_memory': total_conversations,
            'hippo_keywords': hippo_stats['words'],
            'total_neurons': hippo_stats['neurons'],
            'total_synapses': hippo_stats['synapses']
        }
    
    def _extract_keywords(self, text):
        """
        Extract keywords from text (improved version)
        
        Handles:
        - Case preservation (GNJz stays GNJz)
        - Spacing variations (내이름 = 내 이름)
        - Numbers and years
        - Korean particle removal
        """
        import re
        
        if not text:
            return []
        
        # Extract important patterns (years, numbers, names)
        keywords = []
        
        # 1. Extract uppercase words (likely names: GNJz, KAIST, etc.)
        uppercase_words = re.findall(r'\b[A-Z][A-Za-z0-9]*\b', text)
        keywords.extend(uppercase_words)
        keywords.extend([w.lower() for w in uppercase_words])  # Also add lowercase versions
        
        # 2. Extract years (4-digit numbers or XX년)
        years = re.findall(r'\d{2,4}년?', text)
        keywords.extend(years)
        
        # 3. Extract numbers
        numbers = re.findall(r'\d+', text)
        keywords.extend(numbers)
        
        # 4. Korean word extraction (case-insensitive)
        words = text.lower().split()
        
        # Filter stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                     'to', 'of', 'and', 'or', 'in', 'on', 'at',
                     '은', '는', '이', '가', '을', '를', '의', '에', '와', '과',
                     '도', '만', '부터', '까지', '이다', '입니다', '있다', '없다',
                     '나는', '저는', '제', '뭐야', '뭐', '야'}
        
        for w in words:
            # Remove common particles
            w_clean = w.rstrip('은는이가을를의에와과도만부터까지야이야?')
            if w_clean not in stopwords and len(w_clean) > 1:
                keywords.append(w_clean)
                
                # Add spacing variations for Korean
                if len(w_clean) > 2 and any('\uac00' <= c <= '\ud7a3' for c in w_clean):
                    # Extract all substrings (내이름 → 이름, 내재진 → 재진)
                    if w_clean.startswith('내'):
                        suffix = w_clean[1:]  # 내이름 → 이름, 내재진 → 재진
                        if suffix not in stopwords:
                            keywords.append(suffix)
                    
                    # Also extract common Korean compound words
                    # 이름, 나이, 직업, 전화 등
                    common_words = ['이름', '나이', '직업', '전화', '이메일', '주소']
                    for common in common_words:
                        if common in w_clean:
                            keywords.append(common)
        
        # 5. Add full text as keyword for exact matching
        keywords.insert(0, text[:60])
        
        # Return unique keywords (top 10)
        return list(dict.fromkeys(keywords))[:10]
    
    def _compute_importance(self, text, keywords):
        """
        Compute importance score (0.0 ~ 1.0)
        
        Factors:
        - Has factual information (numbers, names, etc.)
        - Questions are LESS important
        - Statements with "is/are" structure are more important
        """
        import re
        
        # Check for numbers/years (factual information)
        has_numbers = bool(re.search(r'\d{2,4}', text))
        number_score = 0.5 if has_numbers else 0.0
        
        # Check for names (patterns like: X이야, X야, X입니다, X님)
        # Korean names typically 2-4 syllables
        name_patterns = [
            r'([가-힣]{2,4})(이야|야|입니다|님|이에요|예요)',  # 재진이야, GNJz야
            r'이름은\s*([가-힣A-Za-z]{2,10})',  # 이름은 재진
        ]
        has_name = any(re.search(pattern, text) for pattern in name_patterns)
        name_score = 0.5 if has_name else 0.0
        
        # Check for identity keywords
        identity_keywords = ['이름', '나이', '직업', '전화', '이메일', '주소', '생년월일']
        has_identity = any(keyword in text for keyword in identity_keywords)
        identity_score = 0.3 if has_identity else 0.0
        
        # Questions are LESS important than statements
        is_question = '?' in text or '뭐' in text or '무엇' in text or '몇' in text or '기억하니' in text
        question_penalty = -0.4 if is_question else 0.0
        
        importance = number_score + name_score + identity_score + question_penalty + 0.2  # Base score
        
        return max(0.0, min(1.0, importance))  # Clamp to 0-1
    
    def consolidate(self):
        """
        Sleep consolidation: strengthen important memories
        """
        # Get high-importance conversations
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT keywords FROM conversations
            WHERE importance > 0.7
            ORDER BY timestamp DESC
            LIMIT 20
        """)
        
        important_keywords = []
        for row in cursor.fetchall():
            important_keywords.extend(row[0].split(','))
        
        # Re-learn important keywords (strengthening)
        for kw in set(important_keywords):
            if kw:
                self.hippo.learn(kw)
        
        # Deep sleep consolidation
        self.hippo.sleep(cycles=30)
    
    def archive_old_conversations(self, days_old=30):
        """
        Archive conversations older than N days
        (Move from SQLite to JSON archive)
        """
        # TODO: Implement archiving to reduce SQLite size
        pass
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 babyHippo Pro - Conversation Memory Test")
    print("=" * 60)
    
    # Create memory system
    memory = ConversationMemory()
    
    # Simulate conversations
    print("\n📝 Learning conversations...")
    memory.learn(
        "나는 오늘 병원에 가서 건강검진을 받았어",
        ai_response="건강검진 결과는 어떠셨나요?",
        context="health"
    )
    
    memory.learn(
        "의사 선생님이 건강하다고 했어. 다행이야",
        ai_response="다행이네요! 정기적인 검진이 중요합니다.",
        context="health"
    )
    
    memory.learn(
        "저녁에 친구들이랑 영화 보러 갔어",
        ai_response="어떤 영화를 보셨나요?",
        context="entertainment"
    )
    
    # Recall
    print("\n🔍 Recalling conversations...")
    results = memory.recall("병원", max_results=3)
    
    for r in results:
        print(f"\n[{r['timestamp']}] ({r['context']})")
        print(f"User: {r['user_msg']}")
        print(f"Keywords: {r['keywords']}")
        print(f"Importance: {r['importance']:.2f}")
    
    # Stats
    print("\n📊 Memory Statistics:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

