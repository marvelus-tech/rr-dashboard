#!/usr/bin/env python3
"""
Generate the premium interactive HTML dashboard from cumulative batch data.
Features: status management, filtering, localStorage persistence, copy prompts.
"""
import json
import hashlib
import base64
from datetime import datetime

DATA_DIR = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/data"
ALL_BATCHES_JSON = f"{DATA_DIR}/all-batches.json"
OUTPUT_HTML = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/dashboard.html"

STATUS_COLORS = {
    "New": "#86868b",
    "Researching": "#5b8bba",
    "Building": "#c9a96e",
    "Live": "#5bbaa9",
    "Rented": "#a574d4",
    "Paused": "#d4965b",
    "Declined": "#c75d5d"
}

STATUS_OPTIONS = ["New", "Researching", "Building", "Live", "Rented", "Paused", "Declined"]


def get_opportunity_id(op):
    """Generate unique ID for an opportunity."""
    raw = f"{op.get('niche','')}-{op.get('city','')}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def load_all_opportunities():
    try:
        with open(ALL_BATCHES_JSON, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
    all_ops = []
    for batch in data.get("batches", []):
        for op in batch.get("opportunities", []):
            op["batch_date"] = batch.get("date", "unknown")
            op["batch_week"] = batch.get("week", 0)
            op["id"] = get_opportunity_id(op)
            all_ops.append(op)
    
    # Default sort: newest first (by batch_week desc, then score desc)
    all_ops.sort(key=lambda x: (-x.get("batch_week", 0), -x.get("opportunity_score", 0)))
    
    for i, op in enumerate(all_ops, 1):
        op["display_rank"] = i
    return all_ops


def build_seo_section(seo):
    """Build SEO analytics HTML section."""
    if not seo or len(seo) == 0:
        return '<div class="seo-section"><div class="seo-verification">⚠️ SEO data not available</div></div>'
    
    kd = seo.get("keyword_difficulty", 0)
    kd_color = "#5bbaa9" if kd < 20 else "#c9a96e" if kd < 40 else "#c75d5d"
    kd_label = "Easy" if kd < 20 else "Moderate" if kd < 40 else "Hard"
    
    sv = seo.get("search_volume", 0)
    sv_label = "Low" if sv < 20 else "Medium" if sv < 60 else "High"
    
    seo_op = seo.get("seo_opportunity_score", 0)
    seo_op_color = "#5bbaa9" if seo_op >= 70 else "#c9a96e" if seo_op >= 40 else "#c75d5d"
    
    return f'''<div class="seo-section">
                <div class="seo-header">
                    <span class="seo-title">SEO Analytics</span>
                    <span class="seo-badge" style="background:{seo_op_color}20;color:{seo_op_color}">{seo_op}/100</span>
                </div>
                <div class="seo-grid">
                    <div class="seo-metric">
                        <div class="seo-metric-value" style="color:{kd_color}">{kd}</div>
                        <div class="seo-metric-label">Keyword Difficulty<br><span style="color:{kd_color};font-size:11px">{kd_label}</span></div>
                    </div>
                    <div class="seo-metric">
                        <div class="seo-metric-value">{sv}</div>
                        <div class="seo-metric-label">Search Volume<br><span style="font-size:11px">{sv_label}</span></div>
                    </div>
                    <div class="seo-metric">
                        <div class="seo-metric-value">{seo.get("competitor_da", "N/A")}</div>
                        <div class="seo-metric-label">Competitor DA</div>
                    </div>
                    <div class="seo-metric">
                        <div class="seo-metric-value">{seo.get("content_gap_score", "N/A")}</div>
                        <div class="seo-metric-label">Content Gap</div>
                    </div>
                </div>
                <div class="seo-details">
                    <div class="seo-detail"><span class="seo-detail-label">Competition:</span> {seo.get("competition_level", "N/A")}</div>
                    <div class="seo-detail"><span class="seo-detail-label">Backlinks:</span> {seo.get("backlink_estimate", "N/A")}</div>
                    <div class="seo-detail"><span class="seo-detail-label">Map Pack:</span> {seo.get("map_pack_status", "N/A")}</div>
                </div>
                <div class="seo-verification">⚠️ Estimated metrics — verify with Ahrefs/Mangools</div>
            </div>'''


def build_card(op, rank):
    """Build a single opportunity card HTML."""
    op_id = op.get("id", "")
    status = op.get("status", "New")
    status_color = STATUS_COLORS.get(status, "#86868b")
    
    priority = op.get("priority", "Monitor")
    priority_dot = "#86868b"
    if priority == "Start Now":
        priority_dot = "#5bbaa9"
    elif priority == "Research Further":
        priority_dot = "#c9a96e"
    
    urgency = op.get("urgency", 5)
    urgency_pct = urgency * 10
    urgency_color = "#c75d5d" if urgency >= 8 else "#c9a96e" if urgency >= 5 else "#5bbaa9"
    urgency_text = "Emergency service — immediate response needed" if urgency >= 8 else "High priority — same-day response" if urgency >= 5 else "Standard — schedule within 24-48hrs"
    
    recurring = op.get("recurring", False)
    recurring_icon_color = "#5bbaa9" if recurring else "#c75d5d"
    recurring_icon_path = "M5 13l4 4L19 7" if recurring else "M6 18L18 6M6 6l12 12"
    recurring_text = "Yes" if recurring else "No"
    
    domains = op.get("domain_suggestions", [])
    if domains:
        domains_html = "".join([f'<span class="domain-tag">{d}</span>' for d in domains[:2]])
    else:
        domains_html = '<span class="domain-tag domain-tag-empty">No domain ideas yet</span>'

    action_steps = [step for step in op.get("action_plan", []) if step]
    first_action_step = action_steps[0] if action_steps else "Research this niche and city to validate competition first."
    extra_action_steps = action_steps[1:]
    extra_steps_count = len(extra_action_steps)
    action_toggle_label = f"Show {extra_steps_count} more step" + ("s" if extra_steps_count != 1 else "")
    first_step_html = f'<li class="action-step-primary">{first_action_step}</li>'
    extra_steps_html = "".join([f'<li>{step}</li>' for step in extra_action_steps])
    action_toggle_html = ""
    if extra_steps_count > 0:
        action_toggle_html = f'''<button class="action-toggle" type="button" aria-expanded="false" aria-controls="action-extra-{op_id}" onclick="toggleActionPlan('{op_id}', this)">{action_toggle_label}</button>'''
    
    status_options_html = "".join([
        f'<option value="{s}" {"selected" if s == status else ""}>{s}</option>'
        for s in STATUS_OPTIONS
    ])
    
    batch_week = op.get("batch_week", 0)
    batch_date = op.get("batch_date", "")
    date_badge = f'<span class="date-badge">Week {batch_week} · {batch_date}</span>' if batch_date else ''
    
    # Encode web prompt as base64
    prompt_raw = op.get("web_prompt", "")
    prompt_b64 = base64.b64encode(prompt_raw.encode("utf-8")).decode("utf-8") if prompt_raw else ""
    
    seo_html = build_seo_section(op.get("seo", {}))
    notes = op.get("notes", "").strip()
    notes_html = f'<div class="notes">{notes}</div>' if notes else ''
    location_reasoning = op.get("location_reasoning", "").strip()
    location_reasoning_html = f'''<div class="location-reasoning">
                <details>
                    <summary>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 16v-4M12 8h.01"/>
                        </svg>
                        Why This Location
                    </summary>
                    <div class="location-reasoning-content">
                        {location_reasoning or "Location selected based on market size and niche fit."}
                    </div>
                </details>
            </div>'''

    card_html = f'''<div class="opportunity-card" data-status="{status.lower()}" data-id="{op_id}" data-batch-week="{batch_week}" data-score="{op.get('opportunity_score', 0)}" style="animation-delay: {min(rank * 0.03, 0.5)}s">            <div class="card-header">
                <div class="header-left">
                    {date_badge}
                </div>
                <div class="header-actions">
                    <button class="copy-btn" data-prompt-b64="{prompt_b64}" onclick="copyPrompt(this)" title="Copy AI Developer Prompt">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                        <span>Prompt</span>
                    </button>
                    <span class="score-badge">{op.get("opportunity_score", 0)}<span class="score-denominator">/10</span></span>
                </div>
            </div>
            <div class="niche-title">{op.get("niche", "")}</div>
            <div class="city-subtitle">
                <svg class="icon-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {op.get("city", "")}
            </div>
            {location_reasoning_html}
            <div class="status-row">
                <span class="status-badge" style="background:{status_color}20;color:{status_color};border:1px solid {status_color}40" id="badge-{op_id}">{status}</span>
                <select class="status-select" data-id="{op_id}" onchange="updateStatus(this)">
                    {status_options_html}
                </select>
            </div>
            <div class="priority-row">
                <span class="priority-dot" style="background:{priority_dot}"></span>
                <span class="priority-badge">{priority}</span>
            </div>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Monthly Fee</div>
                    <div class="metric-value">${op.get("monthly_fee", 0):,.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Avg Job Value</div>
                    <div class="metric-value">${op.get("avg_job_value", 0):,}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Lead Value</div>
                    <div class="metric-value">${op.get("lead_value", 0):,.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Recurring</div>
                    <div class="metric-value recurring-indicator">
                        <svg class="icon-check" viewBox="0 0 24 24" fill="none" stroke="{recurring_icon_color}" stroke-width="2.5"><path d="{recurring_icon_path}"/></svg>
                        {recurring_text}
                    </div>
                </div>
            </div>
            <div class="urgency-row" title="{urgency_text}">
                <span class="urgency-label">Urgency: {urgency}/10</span>
                <div class="urgency-bar"><div class="urgency-fill" style="width:{urgency_pct}%;background:{urgency_color}"></div></div>
            </div>
            <div class="urgency-explanation">{urgency_text}</div>
            {notes_html}
            {seo_html}
            <div class="domain-suggestions">
                <div class="domain-label">Domain Ideas</div>
                <div class="domain-tags">{domains_html}</div>
            </div>
            <div class="action-plan" data-expanded="false">
                <div class="action-plan-header">
                    <svg class="action-plan-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>
                    <span class="action-label">Action Plan</span>
                </div>
                <ol class="action-plan-list">{first_step_html}</ol>
                <ol class="action-plan-list action-plan-extra" id="action-extra-{op_id}">{extra_steps_html}</ol>
                {action_toggle_html}
            </div>
        </div>'''
    
    return card_html


def generate_dashboard_html(opportunities):
    total_ops = len(opportunities)
    avg_fee = sum(op.get("monthly_fee", 0) for op in opportunities) / max(total_ops, 1)
    avg_score = sum(op.get("opportunity_score", 0) for op in opportunities) / max(total_ops, 1)
    start_now_count = sum(1 for op in opportunities if op.get("priority") == "Start Now")
    
    avg_seo_score = 0
    if opportunities:
        seo_scores = [op.get("seo", {}).get("seo_opportunity_score", 0) for op in opportunities if op.get("seo")]
        if seo_scores:
            avg_seo_score = sum(seo_scores) / len(seo_scores)
    
    filter_buttons = "".join([
        f'<button class="filter-btn active" data-filter="all">All ({total_ops})</button>'
    ] + [
        f'<button class="filter-btn" data-filter="{s.lower()}">{s} (0)</button>'
        for s in STATUS_OPTIONS
    ])
    
    sort_buttons = '''<button class="sort-btn active" data-sort="recent">Recently Added</button>
        <button class="sort-btn" data-sort="score">Highest Score</button>'''
    
    cards_html = [build_card(op, i) for i, op in enumerate(opportunities, 1)]
    cards_combined = "\n".join(cards_html)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rank & Rent — Opportunity Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --bg: #0a0a0f;
            --surface: #141419;
            --border: rgba(255,255,255,0.06);
            --text-primary: #f5f5f7;
            --text-secondary: #86868b;
            --accent: #d4a574;
            --font: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
            --success: #5bbaa9;
            --warning: #c9a96e;
            --danger: #c75d5d;
        }}
        
        body {{ font-family: var(--font); background: var(--bg); color: var(--text-primary); min-height: 100vh; -webkit-font-smoothing: antialiased; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 48px 48px 80px; }}
        @media (max-width: 768px) {{ .container {{ padding: 24px 24px 48px; }} }}
        
        /* Header */
        .header {{ margin-bottom: 48px; }}
        .header h1 {{ font-size: 48px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 12px; }}
        .header .subtitle {{ font-size: 17px; color: var(--text-secondary); font-weight: 400; margin-bottom: 8px; }}
        .header .date {{ font-size: 14px; color: var(--text-secondary); opacity: 0.7; }}
        @media (max-width: 768px) {{ .header h1 {{ font-size: 32px; }} }}
        
        /* Filter Bar */
        .filter-bar {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; padding: 20px; background: rgba(20, 20, 25, 0.6); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 16px; }}
        .filter-btn {{ padding: 8px 16px; border-radius: 100px; border: 1px solid rgba(255,255,255,0.08); background: transparent; color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s; font-family: var(--font); }}
        .filter-btn:hover {{ border-color: rgba(255,255,255,0.15); color: var(--text-primary); }}
        .filter-btn.active {{ background: rgba(212, 165, 116, 0.15); color: var(--accent); border-color: rgba(212, 165, 116, 0.3); }}
        
        /* Sort Bar */
        .sort-bar {{ display: flex; align-items: center; gap: 8px; margin-bottom: 32px; padding: 16px 20px; background: rgba(20, 20, 25, 0.4); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 12px; }}
        .sort-label {{ font-size: 13px; color: var(--text-secondary); font-weight: 500; margin-right: 4px; }}
        .sort-btn {{ padding: 6px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); background: transparent; color: var(--text-secondary); font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.2s; font-family: var(--font); }}
        .sort-btn:hover {{ border-color: rgba(255,255,255,0.15); color: var(--text-primary); }}
        .sort-btn.active {{ background: rgba(91, 186, 169, 0.15); color: var(--success); border-color: rgba(91, 186, 169, 0.3); }}
        
        /* Stats Bar */
        .stats-bar {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; margin-bottom: 48px; }}
        @media (max-width: 768px) {{ .stats-bar {{ grid-template-columns: repeat(2, 1fr); }} }}
        
        .stat-card {{ background: rgba(20, 20, 25, 0.6); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 16px; padding: 28px; transition: all 0.3s; }}
        .stat-card:hover {{ border-color: rgba(255,255,255,0.1); transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
        .stat-number {{ font-size: 36px; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; line-height: 1; margin-bottom: 8px; }}
        .stat-label {{ font-size: 13px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 500; }}
        
        /* Grid */
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 24px; }}
        @media (max-width: 920px) {{ .grid {{ grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }} }}
        @media (max-width: 640px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        
        /* Opportunity Card */
        .opportunity-card {{ background: rgba(20, 20, 25, 0.6); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 16px; padding: 28px; position: relative; overflow: hidden; opacity: 0; transform: translateY(12px); animation: cardIn 0.5s forwards; transition: all 0.3s; display: flex; flex-direction: column; }}
        .opportunity-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.1); }}
        .opportunity-card.hidden {{ display: none; }}
        @keyframes cardIn {{ to {{ opacity: 1; transform: translateY(0); }} }}
        
        .opportunity-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--accent); opacity: 0.5; }}
        
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }}
        .header-left {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .date-badge {{ font-size: 11px; color: var(--text-secondary); opacity: 0.7; font-weight: 500; letter-spacing: 0.02em; }}
        .header-actions {{ display: flex; align-items: center; gap: 12px; }}
        .copy-btn {{ display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.03); color: var(--text-secondary); font-size: 12px; font-weight: 500; font-family: var(--font); cursor: pointer; transition: all 0.2s; }}
        .copy-btn:hover {{ background: rgba(212, 165, 116, 0.1); color: var(--accent); border-color: rgba(212, 165, 116, 0.3); }}
        .copy-btn.copied {{ background: rgba(91, 186, 169, 0.15); color: var(--success); border-color: rgba(91, 186, 169, 0.4); }}
        .copy-btn svg {{ width: 14px; height: 14px; flex-shrink: 0; }}
        .score-badge {{ font-size: 28px; font-weight: 600; letter-spacing: -0.02em; line-height: 1; }}
        .score-denominator {{ font-size: 16px; color: var(--text-secondary); font-weight: 400; }}
        
        .niche-title {{ font-size: 20px; font-weight: 500; margin-bottom: 6px; line-height: 1.3; }}
        .city-subtitle {{ font-size: 14px; color: var(--text-secondary); margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }}
        .icon-pin {{ width: 14px; height: 14px; opacity: 0.7; flex-shrink: 0; }}
        
        /* Status Row */
        .status-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }}
        .status-badge {{ font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 100px; text-transform: uppercase; letter-spacing: 0.03em; transition: all 0.3s; }}
        .status-select {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text-primary); padding: 6px 10px; font-size: 13px; font-family: var(--font); cursor: pointer; outline: none; }}
        .status-select:hover {{ border-color: rgba(255,255,255,0.2); }}
        .status-select option {{ background: var(--surface); color: var(--text-primary); }}
        
        /* Priority */
        .priority-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }}
        .priority-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
        .priority-badge {{ font-size: 12px; font-weight: 500; letter-spacing: 0.03em; }}
        
        /* Metrics */
        .metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }}
        .metric {{ background: rgba(255,255,255,0.03); border-radius: 12px; padding: 16px; }}
        .metric-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 6px; font-weight: 500; }}
        .metric-value {{ font-size: 18px; font-weight: 600; font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }}
        .recurring-indicator {{ display: flex; align-items: center; gap: 6px; }}
        .icon-check {{ width: 16px; height: 16px; flex-shrink: 0; }}
        
        /* Urgency */
        .urgency-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 6px; cursor: help; }}
        .urgency-label {{ font-size: 12px; color: var(--text-secondary); white-space: nowrap; font-variant-numeric: tabular-nums; }}
        .urgency-bar {{ flex: 1; height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; }}
        .urgency-fill {{ height: 100%; border-radius: 2px; transition: width 0.6s; }}
        .urgency-explanation {{ font-size: 11px; color: var(--text-secondary); opacity: 0.6; margin-bottom: 14px; padding-left: 4px; }}
        
        /* Notes */
        .notes {{ font-size: 13px; color: var(--text-secondary); font-style: italic; line-height: 1.5; margin-bottom: 16px; padding: 10px 0 10px 12px; border-left: 3px solid rgba(212, 165, 116, 0.3); }}
        
        /* SEO */
        .seo-section {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
        .seo-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
        .seo-title {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); font-weight: 600; }}
        .seo-badge {{ font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 100px; font-variant-numeric: tabular-nums; }}
        .seo-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }}
        .seo-metric {{ background: rgba(255,255,255,0.03); border-radius: 10px; padding: 14px; text-align: center; }}
        .seo-metric-value {{ font-size: 22px; font-weight: 600; font-variant-numeric: tabular-nums; line-height: 1; margin-bottom: 6px; }}
        .seo-metric-label {{ font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); font-weight: 500; line-height: 1.4; }}
        .seo-details {{ display: flex; flex-wrap: wrap; gap: 8px 16px; margin-bottom: 12px; }}
        .seo-detail {{ font-size: 12px; color: var(--text-secondary); }}
        .seo-detail-label {{ color: var(--text-primary); font-weight: 500; }}
        .seo-verification {{ font-size: 11px; color: var(--text-secondary); opacity: 0.6; font-style: italic; text-align: center; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.04); }}
        
        .location-reasoning {{ margin: 0 0 14px; }}
        .location-reasoning details {{ background: rgba(212, 165, 116, 0.06); border: 1px solid rgba(212, 165, 116, 0.25); border-radius: 10px; overflow: hidden; }}
        .location-reasoning summary {{ display: flex; align-items: center; gap: 6px; list-style: none; cursor: pointer; color: #d4a574; font-size: 12px; font-weight: 600; padding: 8px 10px; user-select: none; }}
        .location-reasoning summary::-webkit-details-marker {{ display: none; }}
        .location-reasoning-content {{ padding: 0 10px 10px; color: #d7c5b1; font-size: 12px; line-height: 1.5; }}

        /* Domains */
        .domain-suggestions {{ margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }}
        .domain-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 8px; font-weight: 500; }}
        .domain-tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
        .domain-tag {{ display: inline-block; background: rgba(212, 165, 116, 0.08); color: var(--accent); border-radius: 6px; padding: 4px 8px; font-size: 12px; font-family: 'SF Mono', 'Monaco', monospace; letter-spacing: -0.01em; }}
        .domain-tag-empty {{ background: rgba(255,255,255,0.03); color: var(--text-secondary); font-family: var(--font); }}
        
        /* Action Plan */
        .action-plan {{ background: rgba(212, 165, 116, 0.04); border: 1px solid rgba(212, 165, 116, 0.1); border-radius: 12px; padding: 16px; margin-top: auto; }}
        .action-plan-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
        .action-plan-icon {{ width: 16px; height: 16px; color: var(--accent); flex-shrink: 0; }}
        .action-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--accent); font-weight: 600; }}
        .action-plan-list {{ padding-left: 0; list-style: none; counter-reset: action-step; margin: 0; }}
        .action-plan-extra {{ counter-reset: action-step 1; max-height: 0; opacity: 0; overflow: hidden; transition: max-height 0.28s ease, opacity 0.22s ease; }}
        .action-plan[data-expanded="true"] .action-plan-extra {{ opacity: 1; max-height: 240px; margin-top: 8px; }}
        .action-plan li {{ font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 8px; padding-left: 24px; position: relative; }}
        .action-plan li:last-child {{ margin-bottom: 0; }}
        .action-plan li::before {{ counter-increment: action-step; content: counter(action-step); position: absolute; left: 0; top: 0; width: 18px; height: 18px; border-radius: 50%; background: rgba(255,255,255,0.08); color: var(--text-secondary); font-size: 10px; font-weight: 600; display: flex; align-items: center; justify-content: center; }}
        .action-step-primary {{ color: var(--text-primary); }}
        .action-toggle {{ margin-top: 10px; border: 0; background: transparent; color: var(--accent); font-size: 12px; font-weight: 600; padding: 8px 2px 2px; cursor: pointer; font-family: var(--font); text-align: left; }}
        .action-toggle:hover {{ color: #e2b98e; }}
        .action-toggle:focus-visible {{ outline: 2px solid rgba(212, 165, 116, 0.4); outline-offset: 2px; border-radius: 6px; }}
        
        /* Footer */
        .footer {{ text-align: center; padding: 60px 20px 20px; color: var(--text-secondary); opacity: 0.5; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Opportunity Dashboard</h1>
            <div class="subtitle">Rank & Rent — Website Landlord Model</div>
            <div class="date">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | {total_ops} opportunities | Avg SEO Score: {avg_seo_score:.0f}</div>
        </div>
        
        <div class="filter-bar">
            {filter_buttons}
        </div>
        
        <div class="sort-bar">
            <span class="sort-label">Sort by:</span>
            {sort_buttons}
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-number">{total_ops}</div>
                <div class="stat-label">Opportunities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${avg_fee:,.0f}</div>
                <div class="stat-label">Avg Monthly Fee</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_score:.1f}</div>
                <div class="stat-label">Avg Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_seo_score:.0f}</div>
                <div class="stat-label">Avg SEO Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{start_now_count}</div>
                <div class="stat-label">Start Now</div>
            </div>
        </div>
        
        <div class="grid">
            {cards_combined}
        </div>
        
        <div class="footer">
            <p>Next batch: Weekly on Sundays at 9:00 AM (AEST)</p>
            <p>Status changes persist in browser — click dropdown on any card</p>
        </div>
    </div>
    
    <script>
        const STORAGE_KEY = 'rr-niche-statuses';
        
        function loadStatuses() {{
            try {{
                return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{{}}');
            }} catch {{
                return {{}};
            }}
        }}
        
        function saveStatuses(statuses) {{
            localStorage.setItem(STORAGE_KEY, JSON.stringify(statuses));
        }}
        
        function updateStatus(select) {{
            const id = select.dataset.id;
            const newStatus = select.value;
            const statuses = loadStatuses();
            statuses[id] = newStatus;
            saveStatuses(statuses);
            
            const badge = document.getElementById('badge-' + id);
            const colors = {{
                'New': '#86868b',
                'Researching': '#5b8bba',
                'Building': '#c9a96e',
                'Live': '#5bbaa9',
                'Rented': '#a574d4',
                'Paused': '#d4965b',
                'Declined': '#c75d5d'
            }};
            const color = colors[newStatus] || '#86868b';
            badge.textContent = newStatus;
            badge.style.background = color + '20';
            badge.style.color = color;
            badge.style.borderColor = color + '40';
            
            const card = select.closest('.opportunity-card');
            card.dataset.status = newStatus.toLowerCase();
            
            updateFilterCounts();
        }}
        
        async function copyPrompt(btn) {{
            const b64 = btn.dataset.promptB64;
            if (!b64) {{
                btn.textContent = 'No prompt';
                setTimeout(() => btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg><span>Prompt</span>', 2000);
                return;
            }}
            const prompt = atob(b64);
            try {{
                await navigator.clipboard.writeText(prompt);
                const originalHTML = btn.innerHTML;
                btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg><span>Copied!</span>';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('copied');
                }}, 2000);
            }} catch (err) {{
                console.error('Failed to copy:', err);
                btn.textContent = 'Copy Failed';
                setTimeout(() => {{
                    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg><span>Prompt</span>';
                }}, 2000);
            }}
        }}
        
        function toggleActionPlan(opId, btn) {{
            const card = btn.closest('.action-plan');
            const extraList = document.getElementById('action-extra-' + opId);
            if (!card || !extraList) return;

            const isExpanded = card.dataset.expanded === 'true';
            card.dataset.expanded = isExpanded ? 'false' : 'true';
            btn.setAttribute('aria-expanded', isExpanded ? 'false' : 'true');

            const totalExtra = extraList.querySelectorAll('li').length;
            btn.textContent = isExpanded
                ? `Show ${{totalExtra}} more step${{totalExtra === 1 ? '' : 's'}}`
                : 'Show less';
        }}

        function updateFilterCounts() {{
            const cards = document.querySelectorAll('.opportunity-card');
            const counts = {{}};
            cards.forEach(card => {{
                const status = card.dataset.status;
                counts[status] = (counts[status] || 0) + 1;
            }});
            
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                const filter = btn.dataset.filter;
                if (filter === 'all') {{
                    btn.textContent = `All (${{cards.length}})`;
                }} else {{
                    const count = counts[filter] || 0;
                    const label = filter.charAt(0).toUpperCase() + filter.slice(1);
                    btn.textContent = `${{label}} (${{count}})`;
                }}
            }});
        }}
        
        function sortCards(sortType) {{
            const grid = document.querySelector('.grid');
            const cards = Array.from(document.querySelectorAll('.opportunity-card'));
            
            cards.sort((a, b) => {{
                if (sortType === 'recent') {{
                    const weekA = parseInt(a.dataset.batchWeek) || 0;
                    const weekB = parseInt(b.dataset.batchWeek) || 0;
                    if (weekB !== weekA) return weekB - weekA;
                    const scoreA = parseFloat(a.dataset.score) || 0;
                    const scoreB = parseFloat(b.dataset.score) || 0;
                    return scoreB - scoreA;
                }} else {{
                    const scoreA = parseFloat(a.dataset.score) || 0;
                    const scoreB = parseFloat(b.dataset.score) || 0;
                    return scoreB - scoreA;
                }}
            }});
            
            cards.forEach((card) => {{
                grid.appendChild(card);
            }});
        }}
        
        function applySavedStatuses() {{
            const statuses = loadStatuses();
            Object.entries(statuses).forEach(([id, status]) => {{
                const select = document.querySelector(`select[data-id="${{id}}"]`);
                if (select) {{
                    select.value = status;
                    updateStatus(select);
                }}
            }});
        }}
        
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                document.querySelectorAll('.opportunity-card').forEach(card => {{
                    if (filter === 'all' || card.dataset.status === filter) {{
                        card.classList.remove('hidden');
                    }} else {{
                        card.classList.add('hidden');
                    }}
                }});
            }});
        }});
        
        document.querySelectorAll('.sort-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                sortCards(btn.dataset.sort);
            }});
        }});
        
        document.addEventListener('DOMContentLoaded', () => {{
            applySavedStatuses();
            updateFilterCounts();
        }});
    </script>
</body>
</html>'''
    
    return html


def main():
    opportunities = load_all_opportunities()
    
    if not opportunities:
        print("⚠️ No opportunities found. Run a batch first.")
        opportunities = []
    
    html = generate_dashboard_html(opportunities)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {OUTPUT_HTML}")
    print(f"📊 {len(opportunities)} opportunities rendered")
    
    import subprocess
    try:
        subprocess.run(["open", OUTPUT_HTML], check=False)
        print("🌐 Opened in browser")
    except Exception:
        pass


if __name__ == "__main__":
    main()
