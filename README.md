# PT-OSS HealthCheck Studio

**Platform Audit & Compliance for Enterprise Workflows — v0.1.0 (Pre‑Phase Foundations)**

---

## ภาพรวมผลิตภัณฑ์

**PT-OSS HealthCheck Studio** เป็นแพลตฟอร์ม B2B2C ที่ช่วยองค์กรในการ:

- **ประเมินความสมบูรณ์ของเอกสาร**: ตรวจสอบและวิเคราะห์หลักฐาน (evidence) ตามกฎและมาตรฐานที่กำหนด
- **ประมวลผลและแยกข้อมูล**: อ่านเอกสาร (PDF, Word, อื่นๆ) และแยกข้อมูลโครงสร้างที่ปฏิบัติตามกฎ
- **ประเมินความเชื่อถือได้**: ใช้การตรวจสอบหลายระดับ (tier-based validation) เพื่อให้คะแนนความน่าเชื่อถือ
- **วัฏจักรการทบทวน**: จัดการกระบวนการ peer review และการอนุมัติอย่างมีประสิทธิภาพ

### กรณีการใช้งาน (Use Cases)

1. **องค์กรภาครัฐ**: ตรวจสอบเอกสารยื่นขอโครงการ ใบสมัครอนุญาต หรือรายงานปฏิบัติตามกฎ
2. **สถาบันการเงิน**: ประเมินเอกสารสมัครสินเชื่อ KYC/AML compliance
3. **บริษัทประกันภัย**: ตรวจสอบเอกสารสมัครประกัน คำเรียกร้องค่าสินไหม
4. **องค์กรอื่นๆ**: ระบบการตรวจสอบและทำให้เป็นมาตรฐานสำหรับขั้นตอนธุรกิจใด ๆ ที่ต้องการการตรวจสอบหลักฐาน

### สถาปัตยกรรมแพลตฟอร์ม B2B2C

```
[End-User Portal]  <--\
[Enterprise Portal] <--+-- [API Gateway] --> [Processing Engine]
[Admin Portal]      <--/                     |
                                             +-- [PTIL Validator]
                                             +-- [Document Extractor]
                                             +-- [Rule Engine]
                                             +-- [Audit Trail DB]
```

- **FastAPI** backend สำหรับ multi-tenant APIs
- **PostgreSQL** + JSONB สำหรับการจัดเก็บเอกสารและผลการประเมิน
- **S3-compatible** object storage สำหรับไฟล์เอกสาร
- **Rule Engine** ที่ขยายได้ด้วย JSON-based rule packages
- **PTIL** (Platform Traceability & Integrity Layer) เพื่อความโปร่งใสในการตัดสินใจ

---

## สำคัญ: ไฟล์ที่ลบไปคืออะไร

ในระหว่างการจัดเตรียมพื้นฐาน ได้ลบไฟล์ที่มีความลับออกจาก Git history:
- ข้อมูลการตั้งค่า database จริง
- API keys / credentials ตัวอย่าง
- ข้อมูล compliance templates เฉพาะลูกค้า
- Configuration ของบริษัทตัวอย่างเดิม

ไฟล์เหล่านี้ควรจัดเก็บผ่าน **secret management** ขององค์กร (HashiCorp Vault, AWS Secrets Manager, ฯลฯ) เมื่อปล่อยสู่ production

ชื่อบริษัทภายนอกถูกแทนที่ด้วย "ExampleOrg" เพื่อความเป็นกลาง

## การเริ่มต้นพัฒนาแบบเร็ว

### เงื่อนไขเบื้องต้น

- **OS**: Windows / Linux / macOS
- **Python**: ≥ 3.11
- **Tools**: pip, virtualenv
- **ตัวเลือก**: Docker / docker-compose สำหรับสภาพแวดล้อม isolated

### สัก 5 นาที: ติดตั้งแล้วรัน

```bash
# 1. Clone และเข้า repo
git clone https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio.git
cd PT-OSS-HealthCheck-Studio

# 2. สร้าง virtual environment
python -m venv .venv
.\.venv\Scripts\Activate      # Windows
# หรือ
source .venv/bin/activate       # macOS/Linux

# 3. ติดตั้ง dependencies
pip install -e ".[dev]"

# 4. รันทดสอบ
pytest -v

# 5. รัน API ตัวอย่าง
uvicorn src.ptoss.api.app:app --reload --port 8000
```

API จะทำงานที่ `http://localhost:8000` — เข้า `/docs` เพื่อดู interactive API documentation

---

## โครงสร้างเอกสาร & สถาปัตยกรรม

| ไดเรกทอรี่    | คำอธิบาย                                      |
|---------------|-----------------------------------------------|
| `src/ptoss/`  | โค้ดหลัก (API, data models, rule engine)     |
| `docs/adr/`   | Architecture Decision Records (15 ไฟล์)      |
| `docs/`       | NFR, Data Model, Risk Register, IaC Baseline |
| `schemas/ptil/` | JSON Schema สำหรับ PTIL v0.1.0              |
| `rules/`      | Rule packages (v0.1.0)                       |
| `infra/`      | Infrastructure-as-Code (Terraform skeleton)  |
| `tests/`      | Unit tests (pytest, 19 test cases)          |
| `.github/`    | CI/CD workflows, PR template                |

### ส่วนประกอบหลัก

- **API (`src/ptoss/api/`)**: FastAPI endpoints สำหรับ tenant management, document upload, validation, review
- **Models (`src/ptoss/models.py`)**: Pydantic schemas สำหรับ evidence, rules, metrics, reviews
- **Store (`src/ptoss/store.py`)**: In-memory + PostgreSQL abstraction (audit trail, versioning)
- **Rules (`src/ptoss/rules.py`)**: Rule engine ที่ประเมินหลักฐานตามกฎ
- **Extractors (`src/ptoss/connectors/`)**: Tier-based document extraction (PDF, Word, images)
- **Reporting (`src/ptoss/reporting.py`)**: Generate assessment reports (plain text, DOCX)

---

## สภาพแวดล้อม & การตั้งค่า

### ตัวแปรสภาพแวดล้อม (Environment Variables)

เมื่อปล่อยสู่ production ให้ตั้งค่าผ่าน secret manager:

```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:pass@db-host:5432/ptoss_prod

# Object Storage (S3-compatible)
S3_ENDPOINT=https://s3.amazonaws.com
S3_REGION=us-east-1
S3_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
S3_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET=ptoss-documents

# Document Extraction
OCR_PROVIDER=tesseract  # หรือ google_vision, aws_textract
EXTRACTION_TIMEOUT=300

# AI & Compliance
AI_PROVIDER=openai       # หรือ azure, anthropic
AI_PROVIDER_API_KEY=...
COMPLIANCE_RULES_VERSION=0.1.0

# Security
SECRET_KEY=your-secret-key-for-jwt-signing
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Observability (ตัวเลือก)
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true
JAEGER_ENDPOINT=http://jaeger:6831
```

**เตือน**: ห้ามใส่ credentials ลงใน `.env` หรือ code — ใช้ secret manager เท่านั้น

---

## การพัฒนาและสนับสนุน

### Git Workflow

1. **สร้าง branch** ตามรูปแบบ:
   - `feature/` — ฟีเจอร์ใหม่
   - `fix/` — การแก้ไขบั๊ก
   - `docs/` — อัปเดตเอกสาร
   - `chore/` — การบำรุงรักษา

2. **Commit** ใช้ Conventional Commits:
   ```
   feat(rules): add new validation rule for financial documents
   fix(api): resolve tenant isolation issue in GET /documents
   docs(readme): update setup instructions
   ```

3. **Pull Request** ต้องผ่าน:
   - ✅ Local tests pass (`pytest -v`)
   - ✅ Code follows project DoD (see `docs/DoD.md`)
   - ✅ PR template completed (`.github/PULL_REQUEST_TEMPLATE.md`)

4. **Sync หลังจาก force-push** (ถ้าเกิดขึ้น):
   ```bash
   git fetch origin
   git reset --hard origin/main   # หรือ branch อื่น
   ```

### Testing

```bash
# รัน unit tests ทั้งหมด
pytest -v

# เฉพาะไฟล์เดียว
pytest tests/test_store.py -v

# ด้วยความครอบคลุม (coverage)
pytest --cov=src --cov-report=html
```

**CI/CD**: GitHub Actions จะรัน tests โดยอัตโนมัติเมื่อ push หรือเปิด PR
(ดู `.github/workflows/ci.yml`)

### Documentation

- **ADRs**: `docs/adr/` — สถาปัตยกรรมการตัดสินใจสำหรับการออกแบบหลัก
- **NFR**: `docs/NFR.md` — ข้อกำหนดที่ไม่ใช่เชิงฟังก์ชัน
- **DoD**: `docs/DoD.md` — Definition of Done สำหรับฟีเจอร์
- **Data Model**: `docs/data_model_v0.md` — โครงสร้างข้อมูล
- **Calibration**: `docs/calibration/` — ตัวอย่าง test cases

---

## แผนการพัฒนา (Roadmap)

### Pre‑Phase ✅ (v0.1.0 — เสร็จสมบูรณ์)
- ✅ ADRs และสถาปัตยกรรม
- ✅ PTIL schemas v0.1.0
- ✅ Rule package v0.1.0
- ✅ Unit tests (19 test cases)
- ✅ CI/CD pipeline

### Phase 1 (Q3 2026)
- [ ] Database schema และ migrations (PostgreSQL RLS)
- [ ] Tenant isolation & multi-tenancy
- [ ] Complete API endpoints (auth, document mgmt, validation)
- [ ] Integration tests
- [ ] Docker compose setup

### Phase 2 (Q4 2026)
- [ ] Document extraction library (pdfplumber, python-docx, Tesseract OCR)
- [ ] Advanced rule engine with conditional logic
- [ ] Workflow engine (Temporal integration)
- [ ] Audit trail & compliance logging

### Phase 3 (2027)
- [ ] UI Dashboard (Next.js frontend)
- [ ] Advanced analytics & reporting
- [ ] AI-powered compliance suggestions
- [ ] Multi-language support
- [ ] Enterprise deployment (Kubernetes, Helm)

### Backlog
- [ ] Real-time notifications & webhooks
- [ ] API rate limiting & quotas
- [ ] Custom rule builder UI
- [ ] Integration with external compliance databases
- [ ] Mobile app

---

## ความปลอดภัย

### Best Practices

✅ **ต้องทำ**:
- ใช้ HTTPS/TLS สำหรับการสื่อสาร
- ตรวจสอบ input และ validate schema (Pydantic)
- เข้ารหัสข้อมูลที่เก็บบน disk (at-rest)
- ใช้ JWT tokens พร้อม expiration
- Row-level security (RLS) ใน PostgreSQL สำหรับ multi-tenancy
- Audit log ทุกการเปลี่ยนแปลง
- Rate limiting และ DDoS protection

❌ **ห้ามทำ**:
- ลบข้อมูลที่ได้รับการตรวจสอบแล้ว (keep audit trail)
- เก็บ plaintext passwords
- Commit secrets หรือ API keys ลงใน Git
- Expose stack traces ไปยัง client
- ยอมรับ file upload โดยไม่ validate

### Reporting Security Issues

ถ้าพบช่องโหว่ความปลอดภัย **อย่า**เปิด public issue — ติดต่อทีมโดยตรง:
---

## ลิขสิทธิ์และการใช้งาน

### 📜 License: Elastic License v2 (สำหรับ B2B2C Platform)

นี่คือสิ่งที่เหมาะสำหรับโมเดล B2B2C:

**PT-OSS HealthCheck Studio**  
Copyright © 2026 TAWAN  
ได้รับใบอนุญาตภายใต้ Elastic License v2  
https://www.elastic.co/licensing/elastic-license

### คุณสามารถ:
✅ ใช้งาน, modify, และ deploy ภายใน organization ของคุณ  
✅ ขายบริการของคุณที่ใช้ platform นี้ (B2B, B2B2C)  
✅ Fork และสร้าง proprietary extensions  
✅ ใช้สำหรับระบบภายใน  

### ห้าม:
❌ Redistribute source code โดยตรง  
❌ นำ code ของเรามาขายเป็นผลิตภัณฑ์โดยตรง  
❌ ลบ/ซ่อนข้อมูลลิขสิทธิ์  

### สำหรับองค์กรอื่น:
- ติดต่อสำหรับ **commercial license** ด้วย terms ที่เหมาะสม
- หรือรอการปล่อย future open-source version (ในอนาคต)

### ทำไมเลือก Elastic License สำหรับ B2B2C?

1. **ยืดหยุ่น**: ให้ใช้งาน + modify + deploy + resell บริการ
2. **ปกป้องแนวคิด**: ห้าม redistribute code โดยตรง (ไม่เหมือน MIT)
3. **ธุรกิจเป็นกลาง**: ไม่บังคับเปิดโค้ดการแก้ไข (ไม่เหมือน AGPL)
4. **ชัดเจนสำหรับผู้ใช้**: เข้าใจได้ง่ายว่าอนุญาตอะไร/ห้ามอะไร

---

## ติดต่อและการสนับสนุน

| ช่องทาง | ลิงก์ |
|--------|------|
| 📚 Documentation | https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio/tree/main/docs |
| 🐛 Issue Tracker | https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio/issues |
| 💬 Discussions | https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio/discussions |
| 📧 Email | ptawun@gmail.com |
---

## Attribution

**PT-OSS HealthCheck Studio** — พัฒนาโดย **SA-NOM AI** เพื่อสนับสนุนระบบประเมินความสมบูรณ์ของเอกสารในระดับ enterprise

**Built with**:
- 🐍 Python 3.11+
- ⚡ FastAPI
- 🗄️ PostgreSQL
- 📦 S3-compatible storage
- 🧪 pytest
- 🚀 GitHub Actions CI/CD

---

**Last Updated**: June 2026 | **Version**: 0.1.0 (Pre‑Phase Foundations)
