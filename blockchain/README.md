# 🔗 BabyHippo Blockchain Verification

## Overview

BabyHippo uses **PHAM Sign v4** for:
1. **Proof of Authorship** - 원작자 증명
2. **Contribution Tracking** - 기여도 추적
3. **Revenue Sharing** - 수익 분배

---

## Quick Start

### Sign Your Contribution

```bash
# 기본 서명
python3 pham_sign_v4.py ../babyhippo/brain/_1_thalamus.py \
    --author "YourName" \
    --desc "Added new feature"

# 실행 테스트 포함 서명
python3 pham_sign_v4.py ../babyhippo/brain/_1_thalamus.py \
    --author "YourName" \
    --desc "Bug fix" \
    --exec "python3 {file}"

# 블록체인 보상 포함 (점수 >= 0.5일 때)
python3 pham_sign_v4.py ../babyhippo/brain/_1_thalamus.py \
    --author "YourName" \
    --desc "Major update" \
    --pay
```

---

## Contribution Score System

### 📊 4-Signal Scoring

| Signal | Weight | Description |
|--------|--------|-------------|
| Byte | 25% | 바이트 변경량 |
| Text | 35% | 텍스트 유사도 변화 |
| AST | 30% | 코드 구조 변경 |
| Exec | 10% | 실행 결과 변화 |

### 🏷️ Score Labels

| Label | Score Range | Meaning |
|-------|-------------|---------|
| ⭐ A_HIGH | 0.80 - 1.00 | 높은 기여도 |
| ✅ B_MEDIUM | 0.50 - 0.79 | 중간 기여도 |
| ⚠️ C_LOW | 0.12 - 0.49 | 낮은 기여도 |
| 🚫 SPAM | 0.00 - 0.11 | 스팸 의심 |

---

## Blockchain Structure

### Block Format

```json
{
  "index": 1,
  "timestamp": 1701234567.89,
  "data": {
    "title": "_1_thalamus.py",
    "author": "GNJz",
    "timestamp": "2024-12-01 12:34:56",
    "hash": "abc123...",
    "cid": "QmXyz...",
    "description": "Initial release",
    "score": 0.8542,
    "label": "A_HIGH",
    "signals": {
      "byte": 0.92,
      "text": 0.88,
      "ast": 0.75,
      "exec": 0.90
    },
    "raw_bytes": "...",
    "raw_text": "..."
  },
  "previous_hash": "000...",
  "hash": "def456..."
}
```

### Hash Calculation

```
block_hash = SHA256(
    f"{index}|{prev_hash}|{timestamp}|{SHA256(data)}"
)
```

---

## Revenue Sharing

### Trigger Conditions

- Revenue > $10,000 USD, OR
- Commercial product release

### Distribution

```
Creator (Original Author): 6% of gross revenue
Contributors: Proportional to contribution scores
```

### Payment Methods

1. **Cryptocurrency** (ETH/PHAM token)
2. **Traditional Bank Transfer**
3. **PHAM Token Distribution**

---

## IPFS Integration

### Upload to IPFS

```bash
# Requires IPFS daemon running
ipfs daemon &

# Files are automatically uploaded when signing
python3 pham_sign_v4.py myfile.py --author "Me"
# CID is stored in the block
```

### Verify Content

```bash
ipfs cat <CID>
```

---

## Setup for Blockchain Rewards

### 1. Install Dependencies

```bash
pip install web3 python-dotenv
```

### 2. Create `.env` file

```env
MY_PRIVATE_KEY=your_wallet_private_key
INFURA_URL=https://mainnet.infura.io/v3/your_project_id
PHAM_CONTRACT_ADDRESS=0x...
```

### 3. Run with --pay

```bash
python3 pham_sign_v4.py myfile.py --author "Me" --desc "Update" --pay
```

---

## Chain Files

서명 결과는 파일별로 저장됩니다:

```
blockchain/
├── pham_sign_v4.py           # 서명 도구
├── pham_chain_thalamus.json  # _1_thalamus.py 기록
├── pham_chain_amygdala.json  # _2_amygdala.py 기록
└── ...
```

---

## Verification

### Check Block Integrity

```python
import json
import hashlib

def verify_chain(chain_file):
    with open(chain_file) as f:
        chain = json.load(f)
    
    for i in range(1, len(chain)):
        block = chain[i]
        prev_block = chain[i-1]
        
        # Check previous hash
        if block['previous_hash'] != prev_block['hash']:
            return False, f"Block {i}: Previous hash mismatch"
    
    return True, "Chain valid"

valid, msg = verify_chain("pham_chain_thalamus.json")
print(msg)
```

---

## Contact

- **Creator**: GNJz (Qquarts Co.)
- **Wallet**: `0x99779F19376c4740d4F555083F6dcB2B47C76bF5`
- **License**: PHAM-OPEN v2.0

---

> **"Code is Free. Success is Shared. Ledger is Complete."**

