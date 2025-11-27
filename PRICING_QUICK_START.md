# Pricing System - Quick Start Guide

## 🚀 Get Started in 10 Minutes

### **Step 1: Run Seed Script** (2 minutes)

```bash
cd backend
python seed_pricing_data.py
```

**What this does:**
- Creates 4 pricing plans (Free, Basic, Pro, Enterprise)
- Sets up monthly/yearly prices
- Configures feature quotas
- Seeds OpenAI model pricing

### **Step 2: Start Backend** (1 minute)

```bash
cd backend
uvicorn app.main:app --reload
```

### **Step 3: Test API** (2 minutes)

```bash
# Get all plans
curl http://localhost:8000/pricing/plans

# Check database health
curl http://localhost:8000/admin/health/database

# View revenue vs cost (will show $0 revenue until payment integration)
curl http://localhost:8000/admin/stats/revenue-vs-cost
```

### **Step 4: Start Frontend** (1 minute)

```bash
cd frontend
npm run dev
```

### **Step 5: View Pricing Page** (1 minute)

Visit: http://localhost:3000/pricing

**You should see:**
- ✅ 4 pricing plans
- ✅ Monthly/yearly toggle
- ✅ Feature comparisons
- ✅ Beautiful card design

---

## 📝 How to Add Quota Checks to Your Routes

### **Example: CV Generation**

```python
from app.services.quota_service import QuotaService, QuotaExceededError
from app.services.token_usage_service import TokenUsageService

@router.post("/cv/generate")
async def generate_cv(
    request: CVRequest,
    user_id: str,  # From auth
    db: Session = Depends(get_db)
):
    # 1. Check quota
    try:
        QuotaService.check_and_increment_usage(db, user_id, "cv_generate")
    except QuotaExceededError as e:
        raise HTTPException(402, detail=str(e))
    
    # 2. Call LLM
    response = await openai.chat.completions.create(
        model="gpt-4o",
        messages=[...]
    )
    
    # 3. Log tokens
    TokenUsageService.log_token_usage(
        db=db,
        model_name="gpt-4o",
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        user_id=user_id,
        feature_code="cv_generate"
    )
    
    # 4. Return result
    return {"cv": result}
```

---

## 🎯 Integration Checklist

Apply quota checks to these routes:

- [ ] `/cv/upload` - Feature: `cv_analyze`
- [ ] `/cv/generate` - Feature: `cv_generate`
- [ ] `/rewriter/cv` - Feature: `cv_generate`
- [ ] `/rewriter/cover-letter` - Feature: `cover_letter_generate`
- [ ] `/interview/start` - Feature: `mock_interview`
- [ ] `/career/chat` - Feature: `career_chat_messages`

---

## 📊 Admin Analytics

### **View Revenue vs Cost:**
```bash
curl http://localhost:8000/admin/stats/revenue-vs-cost?days=30
```

### **View User Costs:**
```bash
curl http://localhost:8000/admin/stats/user-costs/{user_id}?days=30
```

### **View Feature Usage:**
```bash
curl http://localhost:8000/admin/stats/features?days=30
```

**⚠️ WARNING:** Admin endpoints are unprotected! Add authentication before production.

---

## 🔧 Common Operations

### **Get User's Current Plan:**
```python
from app.services.plan_service import PlanService

plan = PlanService.get_user_plan(db, user_id)
print(f"User is on {plan.name} plan")
```

### **Check Feature Availability:**
```python
from app.services.quota_service import QuotaService

can_use, reason = QuotaService.can_use_feature(db, user_id, "cv_generate")
if not can_use:
    print(f"Cannot use feature: {reason}")
```

### **Get Usage Statistics:**
```python
from app.services.quota_service import QuotaService

stats = QuotaService.get_usage_stats(db, user_id)
print(f"CV Generation: {stats['features']['cv_generate']['used']}/{stats['features']['cv_generate']['limit']}")
```

---

## 💳 Payment Integration (Next Step)

### **Add Stripe/Paymob:**

1. **Install SDK:**
```bash
pip install stripe  # or paymob-sdk
```

2. **Create Webhook Endpoint:**
```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    # Verify signature
    # Update subscription
    # Record revenue
    pass
```

3. **Update Admin Stats:**
- Fetch actual revenue from Stripe
- Calculate real profit margins
- Track MRR/ARR

---

## 📚 Full Documentation

For complete details, see: `PRICING_SYSTEM_IMPLEMENTATION.md`

Topics covered:
- Full database schema
- All API endpoints
- Service layer details
- Frontend implementation
- Testing guide
- Security notes

---

## ⚡ Quick Reference

### **Feature Codes:**
```
cv_generate                   - CV Generation
cv_analyze                    - CV Analysis
cover_letter_generate         - Cover Letters
mock_interview                - Mock Interviews
career_chat_messages          - Career Chat
```

### **Plans:**
```
free       - $0/month    - Limited features
basic      - $9.99/month - Essential tools
pro        - $29.99/month - Advanced features
enterprise - $99.99/month - Unlimited access
```

### **Key Services:**
```python
PlanService          - Plan lookups
QuotaService         - Usage tracking
TokenUsageService    - Cost tracking
```

---

## 🎉 You're Ready!

✅ Database seeded with plans  
✅ API endpoints working  
✅ Frontend pricing page live  
✅ Services ready for integration  

**Next:** Add quota checks to your feature routes!

---

**Questions?** Check `PRICING_SYSTEM_IMPLEMENTATION.md` for detailed docs.

