# 💳 Stripe Payment Integration Guide

## Quick Setup Guide for CloudEngineered

### Step 1: Create Stripe Account

1. Go to: https://dashboard.stripe.com/register
2. Sign up with your email
3. Verify your email
4. Complete business details

### Step 2: Get API Keys

1. Go to: https://dashboard.stripe.com/test/apikeys
2. Copy your keys:
   ```
   Publishable key: pk_test_XXXXXXXXXXXXXXXXXXXXXXXX
   Secret key: sk_test_YOUR_SECRET_KEY_HERE_SECRET_KEY_HERE
   ```

### Step 3: Set Environment Variables

```bash
# Add to your environment
export STRIPE_PUBLIC_KEY="pk_test_XXXXXXXXXXXXXXXXXXXXXXXX"
export STRIPE_SECRET_KEY="sk_test_YOUR_SECRET_KEY_HERE_SECRET_KEY_HERE"
export STRIPE_WEBHOOK_SECRET="whsec_XXXXXXXXXXXXXXXXXXXXXXXX"
```

### Step 4: Create Products

#### For Premium Subscriptions

1. Go to: https://dashboard.stripe.com/test/products
2. Click "Add Product"

**Pro Tier - Monthly**:
```
Name: CloudEngineered Pro - Monthly
Description: Monthly subscription to Pro features
Price: $29.00 USD
Billing period: Monthly
```

**Pro Tier - Yearly**:
```
Name: CloudEngineered Pro - Yearly
Description: Yearly subscription to Pro features (save 17%)
Price: $290.00 USD
Billing period: Yearly
```

**Enterprise Tier - Monthly**:
```
Name: CloudEngineered Enterprise - Monthly
Description: Monthly subscription to Enterprise features
Price: $99.00 USD
Billing period: Monthly
```

**Enterprise Tier - Yearly**:
```
Name: CloudEngineered Enterprise - Yearly
Description: Yearly subscription to Enterprise features
Price: $990.00 USD
Billing period: Yearly
```

#### For Premium Reports

Create one-time payment products:

**Basic Report**:
```
Name: Premium Report - Basic
Price: $29.00 USD
Type: One-time payment
```

**Standard Report**:
```
Name: Premium Report - Standard
Price: $59.00 USD
Type: One-time payment
```

**Premium Report**:
```
Name: Premium Report - Premium
Price: $99.00 USD
Type: One-time payment
```

#### For Consulting Services

**Discovery Call**:
```
Name: DevOps Consulting - Discovery Call
Price: $149.00 USD
Type: One-time payment
```

**Strategy Session**:
```
Name: DevOps Consulting - Strategy Session
Price: $399.00 USD
Type: One-time payment
```

**Deep Dive**:
```
Name: DevOps Consulting - Deep Dive
Price: $799.00 USD
Type: One-time payment
```

**Team Workshop**:
```
Name: DevOps Consulting - Team Workshop
Price: $1,499.00 USD
Type: One-time payment
```

**Comprehensive Assessment**:
```
Name: DevOps Consulting - Comprehensive
Price: $2,999.00 USD
Type: One-time payment
```

**Retainer**:
```
Name: DevOps Consulting - Monthly Retainer
Price: $1,999.00 USD
Billing period: Monthly
```

### Step 5: Save Price IDs

After creating each product, save the Price ID (starts with `price_`):

```python
# Update in Django settings or database
STRIPE_PRICES = {
    'pro_monthly': 'price_XXXXX',
    'pro_yearly': 'price_YYYYY',
    'enterprise_monthly': 'price_ZZZZZ',
    'enterprise_yearly': 'price_AAAAA',
    'report_basic': 'price_BBBBB',
    'report_standard': 'price_CCCCC',
    'report_premium': 'price_DDDDD',
    # ... consulting packages
}
```

### Step 6: Set Up Webhooks

1. Go to: https://dashboard.stripe.com/test/webhooks
2. Click "Add endpoint"
3. URL: `https://cloudengineered.com/monetization/stripe/webhook/`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`

5. Copy Webhook Signing Secret: `whsec_XXXXXXXXXXXXXXXXXXXXXXXX`

### Step 7: Test Payments

Use test card numbers:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0027 6000 3184`

### Step 8: Go Live

1. Complete business verification
2. Switch to live API keys
3. Create live products (same as test)
4. Update environment variables with live keys

---

## Quick Commands

```bash
# Test Stripe connection
python manage.py shell -c "
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
print('Connected to Stripe:', stripe.Account.retrieve())
"

# Create a test checkout session
python manage.py shell -c "
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price': 'price_XXXXX',  # Your price ID
        'quantity': 1,
    }],
    mode='subscription',
    success_url='https://cloudengineered.com/success',
    cancel_url='https://cloudengineered.com/cancel',
)
print('Checkout URL:', session.url)
"
```

---

## Resources

- **Dashboard**: https://dashboard.stripe.com/
- **Documentation**: https://stripe.com/docs
- **API Reference**: https://stripe.com/docs/api
- **Testing**: https://stripe.com/docs/testing

---

**Estimated Setup Time**: 30-60 minutes
**Support**: support@stripe.com
