# Pricing & Usage System Implementation Guide

## 📋 Overview

This document describes the complete implementation of the dynamic pricing and usage tracking system for the AI Interview & Career Coach SaaS application.

**Date:** November 24, 2024  
**Status:** ✅ Complete - Ready for Production (with caveats)  
**Database:** Neon Postgres (dynamic plans) + SQLAlchemy ORM

---

## 🎯 What Was Implemented

### **Core Features:**
1. ✅ **Dynamic Pricing Plans** - Plans stored in database, not hard-coded
2. ✅ **Feature Quotas** - Per-plan limits for each feature
3. ✅ **Usage Tracking** - Real-time tracking of feature usage per user
4. ✅ **Token Usage Logging** - Track OpenAI API costs for profit analysis
5. ✅ **Admin Analytics** - Internal endpoints for revenue vs cost analysis
6. ✅ **Frontend Pricing Page** - Beautiful, responsive pricing UI
7. ✅ **Seed Data Script** - Initialize database with default plans

---

## 📊 Database Schema

### **1. `pricing_plans`** - High-level plan definitions
```sql
CREATE TABLE pricing_plans (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,      -- 'free', 'basic', 'pro', 'enterprise'
    name VARCHAR(100) NOT NULL,             -- Display name
    description TEXT,                       -- Marketing description
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Seeded Plans:**
- **Free** - Try the app ($0/month)
- **Basic** - Essential tools ($9.99/month, $99/year)
- **Pro** - Advanced features ($29.99/month, $299/year)
- **Enterprise** - Unlimited access ($99.99/month, $999/year)

### **2. `plan_prices`** - Pricing for each billing period
```sql
CREATE TABLE plan_prices (
    id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES pricing_plans(id) ON DELETE CASCADE,
    billing_period VARCHAR(20) NOT NULL,    -- 'monthly' or 'yearly'
    price_cents INT NOT NULL,               -- Price in cents
    currency VARCHAR(10) DEFAULT 'USD',
    trial_days INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Pricing Strategy:**
- Yearly plans save 17% vs monthly
- Trial periods: 7-30 days based on plan

### **3. `plan_features`** - Feature quotas per plan
```sql
CREATE TABLE plan_features (
    id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES pricing_plans(id) ON DELETE CASCADE,
    feature_code VARCHAR(50) NOT NULL,      -- 'cv_generate', 'mock_interview', etc.
    monthly_quota INT,                      -- NULL = unlimited, 0 = disabled
    hard_cap BOOLEAN DEFAULT TRUE,          -- Block after limit?
    rollover BOOLEAN DEFAULT FALSE,         -- Carry over unused quota?
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Feature Codes:**
- `cv_generate` - CV Generation
- `cv_analyze` - CV Analysis & ATS Score
- `cover_letter_generate` - Cover Letters
- `motivation_letter_generate` - Motivation Letters
- `mock_interview` - Mock Interviews
- `career_chat_messages` - Career Coaching Chat
- `job_tracking` - Job Application Tracking

**Quota Examples:**
- Free: 2 CVs, 1 interview, 10 chat messages
- Basic: 10 CVs, 5 interviews, 100 chat messages
- Pro: 30 CVs, 20 interviews, unlimited chat
- Enterprise: Unlimited everything

### **4. `user_feature_usage`** - Track usage per billing period
```sql
CREATE TABLE user_feature_usage (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    plan_id INT REFERENCES pricing_plans(id),
    feature_code VARCHAR(50) NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    used_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_feature (user_id, feature_code, period_start)
);
```

**How it works:**
- Row created on first feature use in billing period
- `used_count` incremented on each use
- Compared against `plan_features.monthly_quota`
- Resets when new billing period starts

### **5. `model_pricing`** - LLM model costs
```sql
CREATE TABLE model_pricing (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    input_cost_per_1k DECIMAL(10,6) NOT NULL,   -- USD per 1000 input tokens
    output_cost_per_1k DECIMAL(10,6) NOT NULL,  -- USD per 1000 output tokens
    currency VARCHAR(10) DEFAULT 'USD',
    effective_from TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Seeded Models:**
- **gpt-4o**: $0.0025 / $0.010 per 1K tokens
- **gpt-4o-mini**: $0.00015 / $0.0006 per 1K tokens
- **gpt-4-turbo**: $0.010 / $0.030 per 1K tokens
- **gpt-3.5-turbo**: $0.0005 / $0.0015 per 1K tokens

### **6. `token_usage_log`** - Every LLM API call
```sql
CREATE TABLE token_usage_log (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    plan_id INT REFERENCES pricing_plans(id),
    feature_code VARCHAR(50),
    model_name VARCHAR(100) NOT NULL,
    input_tokens INT NOT NULL,
    output_tokens INT NOT NULL,
    cost_usd DECIMAL(10,6) NOT NULL,
    request_id VARCHAR(100),
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user (user_id, created_at),
    INDEX idx_feature (feature_code, created_at),
    INDEX idx_model (model_name, created_at)
);
```

**Purpose:**
- Calculate total LLM costs
- Compare with revenue for profit analysis
- Track per-user costs
- Identify high-usage users
- Cost breakdown by feature/model

### **7. `subscriptions`** - Updated to reference plans
```sql
CREATE TABLE subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    plan_id INT REFERENCES pricing_plans(id),  -- NEW: Reference to dynamic plan
    billing_period VARCHAR(20) NOT NULL,
    status VARCHAR(50) NOT NULL,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    -- Legacy fields kept for backward compatibility
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 Backend Services

### **1. Plan Service** (`app/services/plan_service.py`)

**Key Functions:**
```python
get_plan_by_code(db, code)              # Get plan by code ('free', 'pro')
get_user_plan(db, user_id)              # Get user's current plan
get_plan_feature(db, plan_id, feature)  # Get specific feature config
create_subscription(db, user_id, plan)  # Create/update subscription
format_plan_for_api(db, plan)           # Format for API response
```

**Example Usage:**
```python
from app.services.plan_service import PlanService

# Get user's plan
plan = PlanService.get_user_plan(db, user_id)

# Check if feature is available
feature = PlanService.get_plan_feature(db, plan.id, "cv_generate")
if feature and feature.monthly_quota:
    print(f"User can generate {feature.monthly_quota} CVs/month")
```

### **2. Quota Service** (`app/services/quota_service.py`)

**Key Functions:**
```python
check_and_increment_usage(db, user_id, feature_code)  # Check + increment
get_usage_stats(db, user_id)                         # Get user's usage
can_use_feature(db, user_id, feature_code)           # Check without increment
reset_usage_for_period(db, user_id)                  # Reset on renewal
```

**Example Usage:**
```python
from app.services.quota_service import QuotaService, QuotaExceededError

try:
    # Check and increment usage
    QuotaService.check_and_increment_usage(db, user_id, "cv_generate")
    # Proceed with CV generation
except QuotaExceededError as e:
    # Show upgrade message
    return {"error": str(e), "upgrade_url": "/pricing"}
```

**Raises:** `QuotaExceededError` when quota exceeded

### **3. Token Usage Service** (`app/services/token_usage_service.py`)

**Key Functions:**
```python
log_token_usage(db, model, input_tokens, output_tokens, ...)  # Log usage
get_user_cost_summary(db, user_id, days=30)                  # User costs
get_total_cost_summary(db, days=30)                          # Total costs
seed_model_pricing(db)                                        # Seed prices
```

**Example Usage:**
```python
from app.services.token_usage_service import TokenUsageService

# After LLM API call
TokenUsageService.log_token_usage(
    db=db,
    model_name="gpt-4o",
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens,
    user_id=user_id,
    feature_code="career_chat",
    request_id=request_id
)
```

---

## 🚀 API Endpoints

### **Pricing Endpoints** (Public)

#### **GET `/pricing/plans`**
Get all active pricing plans.

**Response:**
```json
[
  {
    "code": "pro",
    "name": "Pro",
    "description": "Advanced features for serious career advancement",
    "sort_order": 3,
    "prices": [
      {
        "billing_period": "monthly",
        "price_cents": 2999,
        "currency": "USD",
        "trial_days": 7,
        "display_price": "$29.99"
      },
      {
        "billing_period": "yearly",
        "price_cents": 29900,
        "currency": "USD",
        "trial_days": 14,
        "display_price": "$299.00"
      }
    ],
    "features": [
      {
        "feature_code": "cv_generate",
        "monthly_quota": 30,
        "hard_cap": true,
        "display_quota": "30"
      },
      {
        "feature_code": "career_chat_messages",
        "monthly_quota": null,
        "hard_cap": false,
        "display_quota": "Unlimited"
      }
    ]
  }
]
```

#### **GET `/pricing/plans/{plan_code}`**
Get specific plan details.

#### **GET `/pricing/features`**
Get feature descriptions and icons.

#### **GET `/pricing/compare`**
Get plan comparison view.

### **Admin Endpoints** (⚠️ Protect in production!)

#### **GET `/admin/stats/revenue-vs-cost?days=30`**
Revenue vs cost analysis.

**Response:**
```json
{
  "period_days": 30,
  "total_revenue_usd": 0.00,          // TODO: Integrate Stripe
  "total_llm_cost_usd": 45.23,
  "estimated_profit_usd": -45.23,
  "profit_margin_percent": 0.00,
  "total_requests": 1234,
  "unique_users": 56,
  "avg_cost_per_request": 0.0367,
  "by_model": [...],
  "by_feature": [...],
  "daily_breakdown": [...]
}
```

#### **GET `/admin/stats/user-costs/{user_id}?days=30`**
Per-user cost analysis.

#### **GET `/admin/stats/plans`**
Plan distribution statistics.

#### **GET `/admin/stats/features?days=30`**
Feature usage statistics.

#### **GET `/admin/health/database`**
Database health check.

---

## 🎨 Frontend Implementation

### **Pricing Page** (`frontend/app/pricing/page.tsx`)

**Features:**
- ✅ Dynamic plan fetching from API
- ✅ Monthly/yearly billing toggle
- ✅ Beautiful card-based design
- ✅ Feature comparison per plan
- ✅ Responsive layout
- ✅ Popular plan highlighting
- ✅ FAQ section

**Screenshots:** (see `/frontend/app/pricing/page.tsx`)

**Key Components:**
```typescript
// Fetch plans from API
const fetchPlans = async () => {
  const response = await fetch(`${NEXT_PUBLIC_API_URL}/pricing/plans`);
  const data = await response.json();
  setPlans(data);
};

// Toggle billing period
<button onClick={() => setBillingPeriod("yearly")}>
  Yearly <span>Save 17%</span>
</button>

// Display plan card
{plans.map(plan => (
  <PlanCard
    plan={plan}
    price={getPrice(plan, billingPeriod)}
    popular={plan.code === 'pro'}
  />
))}
```

### **Navigation**
- Added "Pricing" link to navbar (visible to all users)
- Links to `/pricing` page

---

## 📝 Usage Integration Guide

### **How to Integrate Quota Checks into Your Routes**

#### **Step 1: Import Services**
```python
from app.services.quota_service import QuotaService, QuotaExceededError
```

#### **Step 2: Check Quota Before Feature Use**
```python
@router.post("/cv/generate")
async def generate_cv(
    request: CVGenerateRequest,
    user_id: str,  # From auth
    db: Session = Depends(get_db)
):
    try:
        # Check and increment usage
        QuotaService.check_and_increment_usage(
            db=db,
            user_id=user_id,
            feature_code="cv_generate"
        )
        
        # Proceed with CV generation
        result = await cv_service.generate(request)
        return result
        
    except QuotaExceededError as e:
        raise HTTPException(
            status_code=402,  # Payment Required
            detail={
                "error": "Quota exceeded",
                "message": str(e),
                "upgrade_url": "/pricing"
            }
        )
```

#### **Step 3: Log Token Usage After LLM Call**
```python
from app.services.token_usage_service import TokenUsageService

# After OpenAI API call
response = await openai.chat.completions.create(...)

# Log usage
TokenUsageService.log_token_usage(
    db=db,
    model_name=response.model,
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens,
    user_id=user_id,
    feature_code="cv_generate"
)
```

### **Routes That Need Integration:**

1. **CV Generation** (`/cv/generate`)
   - Feature: `cv_generate`
   - Check quota before generation

2. **CV Analysis** (`/cv/upload`, `/cv/analyze`)
   - Feature: `cv_analyze`
   - Check quota on upload

3. **Cover Letter** (`/rewriter/cover-letter`)
   - Feature: `cover_letter_generate`
   - Check quota before generation

4. **Mock Interview** (`/interview/start`)
   - Feature: `mock_interview`
   - Check quota on session creation

5. **Career Chat** (`/career/chat`)
   - Feature: `career_chat_messages`
   - Check quota per message or session

---

## 🛠️ Setup & Deployment

### **Step 1: Initialize Database**

```bash
# Navigate to backend
cd backend

# Run seed script
python seed_pricing_data.py
```

**Expected Output:**
```
🌱 PRICING DATA SEED SCRIPT
===========================================================
Creating Pricing Plans...
  ✅ Created plan: Free
  ✅ Created plan: Basic
  ✅ Created plan: Pro
  ✅ Created plan: Enterprise

Creating Plan Prices...
  ✅ Created price: Free - monthly = $0.00
  ✅ Created price: Basic - monthly = $9.99
  ...

Creating Plan Features...
  ✅ Created: Free - cv_generate: 2
  ✅ Created: Basic - cv_generate: 10
  ...

Creating Model Pricing...
  ✅ Added pricing for gpt-4o
  ✅ Added pricing for gpt-4o-mini
  ...

✅ SEED COMPLETED SUCCESSFULLY!
```

### **Step 2: Verify Database**

```bash
# Start backend
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/pricing/plans
curl http://localhost:8000/admin/health/database
```

### **Step 3: Test Frontend**

```bash
# Start frontend
cd frontend
npm run dev

# Visit pages
http://localhost:3000/pricing
```

---

## 📊 Admin Dashboard Access

### **Important Security Notes:**

⚠️ **The admin endpoints are currently UNPROTECTED!**

**Before production:**
1. Add admin authentication middleware
2. Use role-based access control (RBAC)
3. Restrict by IP address
4. Add API key authentication
5. Use VPN for internal access

**Temporary Access Control:**
```python
# Add to admin.py
from fastapi import Header, HTTPException

async def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")

# Then use:
@router.get("/admin/stats/revenue-vs-cost")
def get_stats(admin_key: str = Depends(verify_admin_key)):
    ...
```

---

## 💰 Revenue Integration (TODO)

### **Stripe/Paymob Webhooks**

**What's needed:**
1. Listen for subscription events
2. Update `subscriptions` table
3. Track revenue in new table or external service
4. Update profit calculations

**Example Stripe Webhook:**
```python
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    # Verify signature
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
    
    if event.type == "customer.subscription.created":
        # Update subscription
        ...
    
    elif event.type == "invoice.payment_succeeded":
        # Record revenue
        ...
    
    return {"status": "success"}
```

---

## 🔬 Testing

### **Manual Testing Checklist:**

**Backend:**
- [ ] Seed data script runs successfully
- [ ] All pricing endpoints return valid data
- [ ] Quota checks work correctly
- [ ] Token usage is logged
- [ ] Admin endpoints return stats

**Frontend:**
- [ ] Pricing page loads plans from API
- [ ] Billing toggle works
- [ ] Plan cards display correctly
- [ ] Mobile responsive

**Integration:**
- [ ] Feature quota enforced on routes
- [ ] Error messages show upgrade prompts
- [ ] Usage stats update in real-time

### **Automated Tests (TODO):**

```python
# test_quota_service.py
def test_quota_enforcement():
    # Create test user with free plan
    # Use feature multiple times
    # Verify QuotaExceededError raised
    pass

def test_token_logging():
    # Make LLM call
    # Verify token_usage_log entry created
    # Verify cost calculated correctly
    pass
```

---

## 📈 Future Enhancements

### **Phase 2:**
- [ ] Stripe/Paymob payment integration
- [ ] Real revenue tracking
- [ ] User dashboard with usage stats
- [ ] Usage alerts (80%, 90%, 100%)
- [ ] Auto-upgrade prompts

### **Phase 3:**
- [ ] Team/organization plans
- [ ] Referral system
- [ ] Volume discounts
- [ ] Custom enterprise pricing
- [ ] API rate limiting

### **Phase 4:**
- [ ] A/B test pricing
- [ ] Dynamic pricing based on demand
- [ ] Seasonal promotions
- [ ] Coupon codes
- [ ] Gift subscriptions

---

## 📁 Files Created/Modified

### **Created:**
1. ✅ `backend/app/models.py` - 7 new models (pricing tables)
2. ✅ `backend/app/services/plan_service.py` - Plan management
3. ✅ `backend/app/services/quota_service.py` - Usage tracking
4. ✅ `backend/app/services/token_usage_service.py` - Cost tracking
5. ✅ `backend/app/routes/pricing.py` - Public pricing API
6. ✅ `backend/app/routes/admin.py` - Admin analytics
7. ✅ `backend/seed_pricing_data.py` - Database seeding
8. ✅ `frontend/app/pricing/page.tsx` - Pricing page UI
9. ✅ `PRICING_SYSTEM_IMPLEMENTATION.md` - This document

### **Modified:**
1. ✅ `backend/app/main.py` - Registered new routers
2. ✅ `frontend/components/Navbar.tsx` - Added pricing link
3. ✅ `backend/app/models.py` - Updated Subscription model

---

## ⚡ Quick Reference

### **Feature Codes:**
```
cv_generate                    - CV Generation
cv_analyze                     - CV Analysis
cover_letter_generate          - Cover Letters
motivation_letter_generate     - Motivation Letters
mock_interview                 - Mock Interviews
career_chat_messages           - Career Chat
job_tracking                   - Job Tracking
```

### **API Endpoints:**
```
GET  /pricing/plans           - All plans
GET  /pricing/plans/{code}    - Specific plan
GET  /pricing/compare         - Comparison view
GET  /admin/stats/revenue-vs-cost  - P&L
GET  /admin/stats/user-costs/{id}  - User costs
GET  /admin/health/database   - DB health
```

### **Common Operations:**
```python
# Get user's plan
plan = PlanService.get_user_plan(db, user_id)

# Check quota
QuotaService.check_and_increment_usage(db, user_id, "cv_generate")

# Log tokens
TokenUsageService.log_token_usage(db, "gpt-4o", 100, 50, user_id, "cv_generate")

# Get usage stats
stats = QuotaService.get_usage_stats(db, user_id)
```

---

## 🎉 Summary

**What's Complete:**
- ✅ Dynamic pricing system
- ✅ Feature quota tracking
- ✅ Token usage logging
- ✅ Admin analytics
- ✅ Beautiful pricing UI
- ✅ Database seeding

**What's Pending:**
- ⏳ Payment integration (Stripe/Paymob)
- ⏳ Admin authentication
- ⏳ Integrate quota checks into ALL routes
- ⏳ User dashboard with usage stats
- ⏳ Automated tests

**Ready for:**
- ✅ Development testing
- ✅ Internal demos
- ✅ Feature development with quotas
- ⚠️  Production (add auth first!)

---

**Questions?** Check the code comments or create an issue!

**Date:** November 24, 2024  
**Version:** 1.0.0

