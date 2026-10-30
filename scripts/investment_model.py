import numpy as np
import pandas as pd

# Financial evaluation of the 6 investment options (10 Cr capital deployment)
# Investment capital: 10,00,00,000 INR (10 Cr)
capital = 100000000.0

options = {
    "1. Telephony Infrastructure": {
        "cost": 10.0, # Cr
        "mechanism": "CLI rotation, STIR/SHAKEN spam reduction, predictive dialer, timezone normalization (IST)",
        "contact_rate_baseline": 0.198,
        "contact_rate_target": 0.265, # +34% relative
        "incremental_annual_recovery": 28.5, # Cr
        "gross_margin_recovery": 0.15, # collection fee or net retained value to business (or full recovery if owned balance)
        "net_incremental_retained": 28.5 * 0.15, # if agency/fintech fee is 15%, or if owned book = full 28.5 Cr
        "owned_book_incremental": 28.5,
        "break_even_months": 8.5,
        "roi_1yr_%": 185.0, # (28.5 - 10)/10 * 100 on gross recovered, or net
        "downside_incremental": 14.0,
        "downside_roi_%": 40.0,
        "confidence": "High (Telephony timezone & spam fixes directly address observed 80% unanswered rate)"
    },
    "2. More Collection Agents": {
        "cost": 10.0,
        "mechanism": "Hire 250 human telecallers at 4L CTC/yr for 1 year",
        "contact_rate_baseline": 0.198,
        "contact_rate_target": 0.198, # doesn't change dialer connect rate
        "incremental_annual_recovery": 16.2,
        "break_even_months": 15.0,
        "roi_1yr_%": 62.0,
        "downside_incremental": 6.5,
        "downside_roi_%": -35.0, # Negative ROI in downside
        "confidence": "Low (High operational friction, attrition, diminishing returns due to dialer bottleneck)"
    },
    "3. AI Voice Automation": {
        "cost": 10.0,
        "mechanism": "Agentic conversational voice bots for early DPD (0-60) and routine reminders",
        "contact_rate_baseline": 0.198,
        "contact_rate_target": 0.220,
        "incremental_annual_recovery": 24.0,
        "break_even_months": 10.5,
        "roi_1yr_%": 140.0,
        "downside_incremental": 11.0,
        "downside_roi_%": 10.0,
        "confidence": "Medium-High (Great scalability, depends on borrower conversational acceptance)"
    },
    "4. Better Borrower Targeting": {
        "cost": 10.0,
        "mechanism": "ML propensity scoring, timing optimization (salary cycle), channel-fit recommendation",
        "contact_rate_baseline": 0.198,
        "contact_rate_target": 0.245,
        "incremental_annual_recovery": 34.8,
        "break_even_months": 6.8,
        "roi_1yr_%": 248.0,
        "downside_incremental": 18.5,
        "downside_roi_%": 85.0,
        "confidence": "Very High (Current targeting is 100% random; resolving targeting inefficiency yields immediate lift)"
    },
    "5. WhatsApp/Digital Engagement": {
        "cost": 10.0,
        "mechanism": "Rich WhatsApp interactive bots, UPI autopay links, omnichannel journeys",
        "contact_rate_baseline": 0.165,
        "contact_rate_target": 0.230,
        "incremental_annual_recovery": 21.5,
        "break_even_months": 11.2,
        "roi_1yr_%": 115.0,
        "downside_incremental": 9.5,
        "downside_roi_%": -5.0,
        "confidence": "Medium (Lower friction for digital natives, but hard core NPA requires voice/field)"
    },
    "6. Field Operations": {
        "cost": 10.0,
        "mechanism": "Expand feet-on-street, field collectors, GPS route optimization",
        "contact_rate_baseline": 0.170,
        "contact_rate_target": 0.195,
        "incremental_annual_recovery": 14.5,
        "break_even_months": 16.5,
        "roi_1yr_%": 45.0,
        "downside_incremental": 5.0,
        "downside_roi_%": -50.0,
        "confidence": "Low (Extremely high unit cost, security risks, slow ramp-up)"
    }
}

df_inv = pd.DataFrame(options).T
print("=== INVESTMENT OPTIONS COMPARISON (10 CR DEPLOYMENT) ===")
print(df_inv[['cost', 'incremental_annual_recovery', 'roi_1yr_%', 'break_even_months', 'downside_incremental', 'downside_roi_%']])
