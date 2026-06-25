# Contributing to PT-OSS HealthCheck Studio

ขอบคุณที่สนใจที่จะมีส่วนร่วมในโปรเจค PT-OSS HealthCheck Studio! 🙏

นี่คือแนวทางเพื่อให้กระบวนการการแก้ไขและการสนับสนุนของเราเป็นระเบียบและมีประสิทธิภาพ

## Code of Conduct

- ให้เคารพกัน พูดชั่วแน่ะด้วยความเคารพและมีเมตตา
- ไม่สามารถยอมรับ harassment, discrimination, หรือ intimidation ของใด ๆ
- โฟกัสที่การสร้างสรรค์ community ที่รวมตัวกัน

## วิธีการมีส่วนร่วม

### 1. Report Bugs

ถ้าพบบั๊ก โปรดสร้าง issue ที่มีรายละเอียด:
- ชื่อ issue ที่ชัดเจน
- ขั้นตอนการทำซ้ำ (reproduction steps)
- ผลที่คาดหวัง vs ผลที่เกิดขึ้นจริง
- Environment (Python version, OS, dependencies)
- Log/stack trace (ถ้ามี)

### 2. Suggest Features

มีแนวคิด feature ใหม่ไหม? สร้าง issue กับ label `enhancement`:
- อธิบาย use case
- เหตุผลว่าทำไมจึงเป็นประโยชน์
- ตัวอย่างการใช้งาน (mockup, pseudo-code)

### 3. Submit Changes

#### Step 1: Fork & Branch

```bash
# Fork the repo on GitHub
git clone https://github.com/YOUR-USERNAME/PT-OSS-HealthCheck-Studio.git
cd PT-OSS-HealthCheck-Studio
git remote add upstream https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio.git

# Create feature branch
git checkout -b feature/your-feature-name
```

#### Step 2: Code

- ทำตามกฎ Python (PEP 8)
- เพิ่ม unit tests สำหรับ feature/fix ใหม่
- เปิดโค้ดของคุณตามที่อธิบายไว้ใน DoD (`docs/DoD.md`)
- ใช้ Conventional Commits สำหรับ commit messages:
  ```
  feat(module): add new feature
  fix(module): resolve bug X
  docs(readme): update installation
  chore(deps): upgrade fastapi
  test(store): add edge case tests
  ```

#### Step 3: Test Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest -v

# Check coverage
pytest --cov=src --cov-report=html

# Run linter (if configured)
# black src tests
# flake8 src tests
```

ทุก test ต้องผ่าน!

#### Step 4: Sync with upstream

```bash
git fetch upstream
git rebase upstream/main
```

#### Step 5: Push & Create PR

```bash
git push origin feature/your-feature-name
```

จากนั้นเปิด Pull Request บน GitHub:
- ชื่อ PR ที่ชัดเจน (เช่น "Add email validation to API")
- อธิบายสิ่งที่เปลี่ยนแปลงและเหตุผล
- Reference any related issues (เช่น "Closes #42")
- มีภาพหรือ demo (ถ้ากำลังเปลี่ยน UI)

### 4. PR Review Process

PR ของคุณจะไป code review โดย maintainers:
- อาจมี feedback ต้องแก้ไข — เพียงแค่ commit และ push เพิ่ม
- อย่ากังวล feedback คือเพื่อให้ code เข้ม ไม่ใช่ส่วนตัว
- ถ้า PR merge แล้ว ขอบคุณ! 🎉

### 5. Development Workflow (Longer Commits)

สำหรับ feature ที่ใหญ่กว่า:

1. เปิด issue หรือ discussion ก่อน หากแจ้งแนวคิด
2. รอการ feedback จาก maintainers
3. ทำงานใน feature branch ของคุณ
4. เปิด draft PR เพื่อให้เห็นความคืบหน้า
5. เปลี่ยนเป็น "Ready for review" เมื่อสำเร็จ

---

## Guidelines

### Code Style

- **Language**: Python 3.11+
- **Framework**: FastAPI + Pydantic
- **Style**: Follow PEP 8
- **Docstrings**: Use Google-style docstrings for public functions

Example:
```python
def validate_evidence(evidence: Evidence, rules: List[Rule]) -> EvaluationResult:
    """
    Validate evidence against a set of rules.
    
    Args:
        evidence: The evidence object to validate.
        rules: List of rules to apply.
        
    Returns:
        EvaluationResult with scores and recommendations.
        
    Raises:
        ValueError: If evidence schema is invalid.
    """
    # implementation
```

### Testing

- **Framework**: pytest
- **Coverage**: Aim for >80% code coverage
- **Naming**: Test functions start with `test_` and describe what they test

Example:
```python
def test_validation_passes_with_complete_evidence():
    """Should return passing score when all required fields present."""
    evidence = Evidence(...)
    result = validate_evidence(evidence, [])
    assert result.passed
```

### Documentation

- ทุก feature ใหม่ต้อง document ใน README หรือ docs/
- ถ้า API endpoint เพิ่มเติม ให้เขียน docstring
- Commit messages ต้องสิ้นสุดด้วย `Co-authored-by: Your Name <email>` (ถ้าต้องการ)

### Commit Messages

```
feat(rules): support dynamic rule composition

- Allow rules to reference other rules
- Add rule dependency resolution
- Update rule-package schema

Closes #123
```

---

## Development Environment

### Local Setup

```bash
# Clone
git clone https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio.git
cd PT-OSS-HealthCheck-Studio

# Virtual environment
python -m venv .venv
.\.venv\Scripts\Activate  # Windows
source .venv/bin/activate   # macOS/Linux

# Install
pip install -e ".[dev]"

# Run tests
pytest -v
```

### IDE Setup (Optional)

**VS Code** (recommended):
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  }
}
```

---

## Additional Resources

- **ADRs**: `docs/adr/` — สถาปัตยกรรมการตัดสินใจ
- **Definition of Done**: `docs/DoD.md` — checklist ก่อนปิด feature
- **Data Model**: `docs/data_model_v0.md` — โครงสร้างข้อมูล
- **GitHub Issues**: https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio/issues

---

## Questions?

- 📧 Email: dev@sanomaiarch.com
- 💬 Start a Discussion: https://github.com/sanom-ai/PT-OSS-HealthCheck-Studio/discussions

ขอบคุณที่ยุ่งเหยิงกับเรา! 🙏

**SA-NOM AI Development Team**
