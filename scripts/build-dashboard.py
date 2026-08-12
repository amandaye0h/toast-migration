#!/usr/bin/env python3
"""Build a static HTML dashboard from data/inventory.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="dark" />
  <title>Toast Migration</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      color-scheme: dark;
      --background: oklch(0.145 0 0);
      --foreground: oklch(0.985 0 0);
      --card: oklch(0.205 0 0);
      --card-foreground: oklch(0.985 0 0);
      --primary: #152c2e;
      --primary-foreground: #ffffff;
      --secondary: oklch(0.269 0 0);
      --secondary-foreground: oklch(0.985 0 0);
      --muted: oklch(0.269 0 0);
      --muted-foreground: oklch(0.708 0 0);
      --accent: #1c3d40;
      --accent-foreground: #ffffff;
      --border: oklch(1 0 0 / 10%);
      --input: oklch(1 0 0 / 15%);
      --ring: #2a5a5e;
      --radius: 0.625rem;
      --teal: #3d7378;
      --teal-bright: #8CD6E5;
      --amber: #F1BC8E;
      --cl: #B8A4E8;
      --bn: #F1BC8E;
      --mmds: #98C379;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, sans-serif;
      background: var(--background);
      color: var(--foreground);
      -webkit-font-smoothing: antialiased;
    }

    .shell {
      width: 100%;
      max-width: 48rem;
      margin: 0 auto;
      padding: 2.5rem 1rem 4rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    @media (min-width: 640px) {
      .shell {
        padding: 3.5rem 1.5rem 5rem;
      }
    }

    header {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .title-block {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    h1 {
      margin: 0;
      font-size: 2.25rem;
      font-weight: 600;
      letter-spacing: -0.025em;
      line-height: 1.1;
    }

    @media (min-width: 640px) {
      h1 { font-size: 3rem; }
    }

    .subtitle {
      margin: 0;
      max-width: 36rem;
      font-size: 1rem;
      line-height: 1.5;
      color: var(--muted-foreground);
    }

    @media (min-width: 640px) {
      .subtitle { font-size: 1.125rem; }
    }

    .meta {
      margin: 0;
      font-size: 0.8125rem;
      color: var(--muted-foreground);
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.75rem;
    }

    @media (min-width: 640px) {
      .stats { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }

    @media (min-width: 900px) {
      .stats { grid-template-columns: repeat(6, minmax(0, 1fr)); }
    }

    .stat {
      background: var(--card);
      color: var(--card-foreground);
      border-radius: calc(var(--radius) * 1.4);
      box-shadow: 0 0 0 1px color-mix(in oklab, var(--foreground) 10%, transparent);
      padding: 0.9rem 1rem;
    }

    .stat-label {
      font-size: 0.75rem;
      color: var(--muted-foreground);
      margin-bottom: 0.35rem;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.02em;
      line-height: 1;
    }

    .search-wrap {
      position: relative;
      max-width: 28rem;
    }

    .search-wrap svg {
      position: absolute;
      top: 50%;
      left: 0.625rem;
      width: 1rem;
      height: 1rem;
      transform: translateY(-50%);
      color: var(--muted-foreground);
      pointer-events: none;
    }

    .search {
      width: 100%;
      height: 2rem;
      border-radius: var(--radius);
      border: 1px solid var(--input);
      background: color-mix(in oklab, var(--input) 30%, transparent);
      color: var(--foreground);
      font: inherit;
      font-size: 0.875rem;
      padding: 0.25rem 0.625rem 0.25rem 2rem;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
    }

    .search::placeholder { color: var(--muted-foreground); }

    .search:focus-visible {
      border-color: var(--ring);
      box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 50%, transparent);
    }

    .tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .tab {
      height: 1.75rem;
      padding: 0 0.75rem;
      border-radius: calc(var(--radius) * 0.8);
      border: 1px solid var(--border);
      background: transparent;
      color: var(--muted-foreground);
      font: inherit;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
    }

    .tab:hover {
      background: color-mix(in oklab, var(--muted) 50%, transparent);
      color: var(--foreground);
    }

    .tab[aria-selected="true"] {
      border-color: var(--border);
      background: var(--muted);
      color: var(--foreground);
    }

    .separator {
      height: 1px;
      background: var(--border);
      border: 0;
      margin: 0;
    }

    .section-label {
      margin: 0;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--muted-foreground);
    }

    .list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .card {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      background: var(--card);
      color: var(--card-foreground);
      border-radius: calc(var(--radius) * 1.4);
      box-shadow: 0 0 0 1px color-mix(in oklab, var(--foreground) 10%, transparent);
      padding: 1rem;
    }

    .card.hidden { display: none; }

    .badges {
      display: flex;
      flex-wrap: wrap;
      gap: 0.375rem;
      align-items: center;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      height: 1.25rem;
      padding: 0 0.5rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 500;
      white-space: nowrap;
      background: var(--muted);
      color: var(--muted-foreground);
      border: 1px solid transparent;
    }

    .badge.outline {
      background: transparent;
      border-color: color-mix(in oklab, var(--teal-bright) 50%, transparent);
      color: var(--teal-bright);
    }

    .badge.warn {
      background: transparent;
      border-color: color-mix(in oklab, var(--amber) 50%, transparent);
      color: var(--amber);
    }

    .card-title {
      margin: 0;
      display: flex;
      align-items: flex-start;
      gap: 0.5rem;
      font-weight: 500;
      line-height: 1.35;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.8125rem;
    }

    .card-title-path {
      flex: 1;
      min-width: 0;
    }

    .copy-btn {
      flex-shrink: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1.5rem;
      height: 1.5rem;
      margin: -0.125rem 0 0;
      padding: 0;
      border: 1px solid var(--border);
      border-radius: calc(var(--radius) * 0.7);
      background: transparent;
      color: var(--muted-foreground);
      cursor: pointer;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
    }

    .copy-btn:hover {
      background: color-mix(in oklab, var(--muted) 50%, transparent);
      color: var(--foreground);
    }

    .copy-btn:focus-visible {
      outline: none;
      border-color: var(--ring);
      box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 50%, transparent);
    }

    .copy-btn.copied {
      color: var(--teal-bright);
      border-color: color-mix(in oklab, var(--teal-bright) 50%, transparent);
    }

    .copy-btn svg {
      width: 0.875rem;
      height: 0.875rem;
    }

    .card-desc {
      margin: 0;
      font-size: 0.875rem;
      line-height: 1.55;
      color: var(--muted-foreground);
    }

    .calls {
      margin: 0.25rem 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 0.35rem;
    }

    .calls li {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.72rem;
      line-height: 1.45;
      color: var(--muted-foreground);
      word-break: break-word;
    }

    .calls .hint {
      color: var(--teal-bright);
    }

    .calls .line {
      color: color-mix(in oklab, var(--foreground) 55%, transparent);
    }

    .empty {
      margin: 0;
      font-size: 0.875rem;
      color: var(--muted-foreground);
    }

    .note {
      margin: 0;
      font-size: 0.8125rem;
      line-height: 1.5;
      color: var(--muted-foreground);
    }

    .note code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.75rem;
      color: color-mix(in oklab, var(--foreground) 80%, transparent);
    }

    footer {
      font-size: 0.8125rem;
      color: var(--muted-foreground);
    }

    footer code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.75rem;
    }

    .chart-card {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      background: var(--card);
      color: var(--card-foreground);
      border-radius: calc(var(--radius) * 1.4);
      box-shadow: 0 0 0 1px color-mix(in oklab, var(--foreground) 10%, transparent);
      padding: 1rem 1.1rem 1.15rem;
    }

    .chart-heading {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .chart-title {
      margin: 0;
      font-size: 0.9375rem;
      font-weight: 600;
      letter-spacing: -0.01em;
    }

    .chart-subtitle {
      margin: 0;
      font-size: 0.75rem;
      color: var(--muted-foreground);
    }

    .bar-chart {
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
    }

    .bar-row {
      display: grid;
      grid-template-columns: minmax(5.5rem, 9.5rem) 1fr auto;
      gap: 0.65rem;
      align-items: center;
    }

    @media (max-width: 520px) {
      .bar-row {
        grid-template-columns: minmax(4.5rem, 7rem) 1fr auto;
        gap: 0.45rem;
      }
    }

    .bar-label {
      font-size: 0.75rem;
      line-height: 1.25;
      color: color-mix(in oklab, var(--foreground) 82%, transparent);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .bar-label.mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.68rem;
    }

    .bar-track {
      height: 0.55rem;
      border-radius: 999px;
      background: color-mix(in oklab, var(--muted) 80%, transparent);
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      border-radius: inherit;
      background: var(--cl);
      width: 0;
      transition: width 0.45s ease;
    }

    .bar-fill.cl { background: var(--cl); }
    .bar-fill.bn { background: var(--bn); }
    .bar-fill.mmds { background: var(--mmds); }

    .bar-value {
      min-width: 1.75rem;
      text-align: right;
      font-size: 0.75rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      color: var(--muted-foreground);
    }

    .donut-layout {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.75rem;
      padding-block: 0.75rem;
    }

    .donut {
      --donut-size: 9rem;
      width: var(--donut-size);
      height: var(--donut-size);
      border-radius: 50%;
      display: grid;
      place-items: center;
      flex-shrink: 0;
      background: var(--muted);
    }

    .donut-hole {
      width: 88%;
      height: 88%;
      border-radius: 50%;
      background: var(--card);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.1rem;
      box-shadow: 0 0 0 1px color-mix(in oklab, var(--foreground) 6%, transparent);
    }

    .donut-total {
      font-size: 1.35rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.02em;
      line-height: 1;
    }

    .donut-total-label {
      font-size: 0.65rem;
      color: var(--muted-foreground);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .donut-legend {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.55rem;
      min-width: 10rem;
      flex: 1;
    }

    .donut-legend li {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 0.55rem;
      align-items: center;
    }

    .donut-swatch {
      width: 0.55rem;
      height: 0.55rem;
      border-radius: 999px;
      background: var(--cl);
    }

    .donut-swatch.cl { background: var(--cl); }
    .donut-swatch.bn { background: var(--bn); }
    .donut-swatch.mmds { background: var(--mmds); }

    .donut-legend-label {
      font-size: 0.75rem;
      color: color-mix(in oklab, var(--foreground) 82%, transparent);
    }

    .donut-legend-value {
      font-size: 0.75rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
      color: var(--muted-foreground);
    }

    .charts {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .charts-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }

    .charts-row .chart-heading {
      text-align: center;
    }

    .charts-row .donut-legend {
      width: 100%;
      max-width: none;
      align-self: stretch;
      min-width: 0;
    }

    @media (max-width: 720px) {
      .charts-row {
        grid-template-columns: 1fr;
      }
    }

    .search-wrap.is-hidden { display: none; }

    [hidden] { display: none !important; }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div class="title-block">
        <h1>Toast Migration</h1>
        <p class="subtitle">Inventory of toast surfaces in metamask-mobile</p>
        <p class="meta" id="meta"></p>
      </div>

      <div class="stats" id="stats"></div>
    </header>

    <div class="tabs" role="tablist" aria-label="Toast systems">
      <button class="tab" role="tab" data-tab="overview" aria-selected="true">Overview</button>
      <button class="tab" role="tab" data-tab="cl" aria-selected="false">Component-library</button>
      <button class="tab" role="tab" data-tab="bn" aria-selected="false">BaseNotification</button>
      <button class="tab" role="tab" data-tab="mmds" aria-selected="false">MMDS</button>
    </div>

    <div class="search-wrap">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.3-4.3"></path>
      </svg>
      <input id="search" class="search" type="search" placeholder="Search files, areas, hints…" aria-label="Search toasts" />
    </div>

    <hr class="separator" />

    <section id="panel-overview" data-panel="overview">
      <div class="charts" id="overview-charts"></div>
    </section>

    <section id="panel-cl" data-panel="cl" hidden>
      <div class="list" style="gap: 1.5rem;">
        <div>
          <p class="note" style="margin-bottom: 0.75rem;">
            Files that import <code>component-library/components/Toast</code> or call <code>ToastService.showToast</code>. Tests and stories excluded.
          </p>
          <p class="section-label" id="cl-count" style="margin-bottom: 0.75rem;"></p>
          <div class="list" id="cl-list"></div>
        </div>
      </div>
    </section>

    <section id="panel-bn" data-panel="bn" hidden>
      <div class="list" style="gap: 1.5rem;">
        <p class="note">
          Legacy notification queue rendered via <code>BaseNotification</code>. Producers enqueue with <code>NotificationManager</code>; consumers render the component.
        </p>
        <div>
          <p class="section-label" style="margin-bottom: 0.75rem;">Producers</p>
          <div class="list" id="bn-producers"></div>
        </div>
        <div>
          <p class="section-label" style="margin-bottom: 0.75rem;">Consumers</p>
          <div class="list" id="bn-consumers"></div>
        </div>
      </div>
    </section>

    <section id="panel-mmds" data-panel="mmds" hidden>
      <div class="list" style="gap: 1.5rem;">
        <div>
          <p class="note" style="margin-bottom: 0.75rem;">
            Files that import <code>toast</code> / <code>Toaster</code> from <code>@metamask/design-system-react-native</code>. Target API for migration. Tests and stories excluded.
          </p>
          <p class="section-label" id="mmds-count" style="margin-bottom: 0.75rem;"></p>
          <div class="list" id="mmds-list"></div>
        </div>
      </div>
    </section>

    <footer>
      Re-scan: <code>python3 scripts/scan-toasts.py && python3 scripts/build-dashboard.py</code>
    </footer>
  </div>

  <script>
    const DATA = __DATA__;

    const scanned = DATA.scannedAt ? new Date(DATA.scannedAt) : null;
    const lastUpdated = scanned && !Number.isNaN(scanned.getTime())
      ? scanned.toLocaleString(undefined, {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
        })
      : (DATA.scannedAt || 'unknown');
    document.getElementById('meta').textContent = `Last updated ${lastUpdated}`;

    const s = DATA.summary;
    document.getElementById('stats').innerHTML = [
      ['component-library files', s.componentLibraryToastFiles],
      ['component-library calls', s.componentLibraryToastCalls],
      ['Base Notification producers', s.baseNotificationProducerFiles],
      ['Base Notification calls', s.baseNotificationProducerCalls],
      ['MMDS toast files', s.mmdsToastFiles ?? 0],
      ['MMDS toast calls', s.mmdsToastCalls ?? 0],
    ].map(([label, value]) => `
      <div class="stat">
        <div class="stat-label">${label}</div>
        <div class="stat-value">${value}</div>
      </div>
    `).join('');

    function esc(str) {
      return String(str ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
    }

    const COPY_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16V4a2 2 0 0 1 2-2h10"/></svg>`;
    const CHECK_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>`;

    function fileTitle(path) {
      return `<h3 class="card-title">
        <span class="card-title-path">${esc(path)}</span>
        <button type="button" class="copy-btn" data-copy="${esc(path)}" aria-label="Copy path" title="Copy path">${COPY_ICON}</button>
      </h3>`;
    }

    function callList(calls) {
      if (!calls?.length) return '';
      return `<ul class="calls">${calls.map((c) => `
        <li>
          <span class="line">L${c.line}</span>${
            c.hint ? ` · <span class="hint">${esc(c.hint)}</span>` : ''
          } · ${esc(c.code)}
        </li>`).join('')}</ul>`;
    }

    function barChart(rows, { mono = false, fillClass = 'cl' } = {}) {
      if (!rows.length) return '<p class="empty">No data.</p>';
      const max = Math.max(...rows.map((r) => r.value), 1);
      return `<div class="bar-chart">${rows.map((r) => `
        <div class="bar-row" title="${esc(r.label)}: ${r.value}">
          <div class="bar-label${mono ? ' mono' : ''}">${esc(r.label)}</div>
          <div class="bar-track">
            <div class="bar-fill ${r.fillClass || fillClass}" style="width:${(r.value / max) * 100}%"></div>
          </div>
          <div class="bar-value">${r.value}</div>
        </div>`).join('')}</div>`;
    }

    const FILL_COLORS = { cl: 'var(--cl)', bn: 'var(--bn)', mmds: 'var(--mmds)' };

    function circleChart(rows, { unit = '' } = {}) {
      if (!rows.length) return '<p class="empty">No data.</p>';
      const total = rows.reduce((sum, r) => sum + (r.value || 0), 0);
      let cursor = 0;
      const stops = rows.map((r) => {
        const fill = FILL_COLORS[r.fillClass] || 'var(--cl)';
        const start = total ? (cursor / total) * 100 : 0;
        cursor += r.value || 0;
        const end = total ? (cursor / total) * 100 : 0;
        return `${fill} ${start}% ${end}%`;
      });
      const gradient = total
        ? `conic-gradient(from -90deg, ${stops.join(', ')})`
        : 'var(--muted)';
      return `<div class="donut-layout">
        <div class="donut" style="background:${gradient}" role="img" aria-label="${esc(unit || 'total')}: ${total}">
          <div class="donut-hole">
            <div class="donut-total">${total}</div>
            ${unit ? `<div class="donut-total-label">${esc(unit)}</div>` : ''}
          </div>
        </div>
        <ul class="donut-legend">${rows.map((r) => `
          <li title="${esc(r.label)}: ${r.value}">
            <span class="donut-swatch ${esc(r.fillClass || 'cl')}"></span>
            <span class="donut-legend-label">${esc(r.label)}</span>
            <span class="donut-legend-value">${r.value}</span>
          </li>`).join('')}</ul>
      </div>`;
    }

    function chartCard(title, subtitle, body) {
      return `<article class="chart-card">
        ${title ? `<div class="chart-heading">
          <h2 class="chart-title">${esc(title)}</h2>
          ${subtitle ? `<p class="chart-subtitle">${esc(subtitle)}</p>` : ''}
        </div>` : ''}
        ${body}
      </article>`;
    }

    function renderOverview() {
      const clCallsByArea = {};
      for (const entry of DATA.componentLibraryToasts || []) {
        clCallsByArea[entry.area] = (clCallsByArea[entry.area] || 0) + (entry.callCount || 0);
      }

      const bnCallsByArea = {};
      for (const entry of DATA.baseNotificationProducers || []) {
        bnCallsByArea[entry.area] = (bnCallsByArea[entry.area] || 0) + (entry.count || 0);
      }

      const systemRows = [
        { label: 'component-library', value: s.componentLibraryToastCalls, fillClass: 'cl' },
        { label: 'BaseNotification', value: s.baseNotificationProducerCalls, fillClass: 'bn' },
        { label: 'MMDS', value: s.mmdsToastCalls ?? 0, fillClass: 'mmds' },
      ];

      const fileRows = [
        { label: 'component-library', value: s.componentLibraryToastFiles, fillClass: 'cl' },
        { label: 'BaseNotification', value: s.baseNotificationProducerFiles, fillClass: 'bn' },
        { label: 'MMDS', value: s.mmdsToastFiles ?? 0, fillClass: 'mmds' },
      ];

      const clAreaFiles = Object.entries(s.componentLibraryByArea || {})
        .map(([label, value]) => ({ label, value }))
        .sort((a, b) => b.value - a.value);

      const clAreaCalls = Object.entries(clCallsByArea)
        .map(([label, value]) => ({ label, value }))
        .sort((a, b) => b.value - a.value);

      const bnAreaCalls = Object.entries(bnCallsByArea)
        .map(([label, value]) => ({ label, value }))
        .sort((a, b) => b.value - a.value);

      const mmdsCallsByArea = {};
      for (const entry of DATA.mmdsToasts || []) {
        mmdsCallsByArea[entry.area] = (mmdsCallsByArea[entry.area] || 0) + (entry.callCount || 0);
      }
      const mmdsAreaCalls = Object.entries(mmdsCallsByArea)
        .map(([label, value]) => ({ label, value }))
        .sort((a, b) => b.value - a.value);

      const topFiles = [...(DATA.componentLibraryToasts || [])]
        .filter((e) => (e.callCount || 0) > 0)
        .sort((a, b) => b.callCount - a.callCount)
        .slice(0, 12)
        .map((e) => ({
          label: e.file.replace(/^app\/components\//, '').replace(/^app\//, ''),
          value: e.callCount,
        }));

      const charts = [
        `<div class="charts-row">
          ${chartCard('Calls by system', 'Total toast / notification call sites', circleChart(systemRows, { unit: 'calls' }))}
          ${chartCard('Files by system', 'Files that produce or host toast usage', circleChart(fileRows, { unit: 'files' }))}
        </div>`,
        chartCard('component-library files by area', 'Where Toast imports live', barChart(clAreaFiles, { fillClass: 'cl' })),
        chartCard('component-library calls by area', 'showToast / ToastService call sites', barChart(clAreaCalls, { fillClass: 'cl' })),
        chartCard('BaseNotification calls by area', 'NotificationManager producer call sites', barChart(bnAreaCalls, { fillClass: 'bn' })),
      ];
      if (mmdsAreaCalls.length) {
        charts.push(chartCard('MMDS calls by area', 'Design-system toast call sites', barChart(mmdsAreaCalls, { fillClass: 'mmds' })));
      }
      charts.push(chartCard('Top files by call count', 'Highest component-library toast call density', barChart(topFiles, { mono: true, fillClass: 'cl' })));

      document.getElementById('overview-charts').innerHTML = charts.join('');

      requestAnimationFrame(() => {
        document.querySelectorAll('#overview-charts .bar-fill').forEach((el) => {
          const w = el.style.width;
          el.style.width = '0';
          requestAnimationFrame(() => { el.style.width = w; });
        });
      });
    }

    function renderCl() {
      const cards = DATA.componentLibraryToasts.map((entry) => {
        const hay = [entry.file, entry.area, entry.role, entry.via, ...entry.calls.map((c) => `${c.hint} ${c.code}`)]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge outline">${esc(entry.role)}</span>
              <span class="badge">${entry.callCount} call${entry.callCount === 1 ? '' : 's'}</span>
            </div>
            ${fileTitle(entry.file)}
            ${callList(entry.calls)}
          </article>`;
      }).join('');

      document.getElementById('cl-list').innerHTML = cards || '<p class="empty">No matches.</p>';
      document.getElementById('cl-count').textContent =
        `${DATA.componentLibraryToasts.length} files · ${s.componentLibraryToastCalls} calls`;
    }

    function renderBn() {
      const producers = DATA.baseNotificationProducers.map((entry) => {
        const hits = entry.hits.map((h) => {
          const label = h.title || h.i18nKeys?.[0] || h.code;
          return `
            <li>
              <span class="line">L${h.line}</span> ·
              <span class="badge warn" style="height:auto;display:inline;">${esc(h.kind)}</span> ·
              <span class="hint">${esc(label)}</span>${
                h.description ? ` — ${esc(h.description)}` : ''
              }
            </li>`;
        }).join('');
        const hay = [entry.file, entry.area, ...entry.hits.flatMap((h) => [h.title, h.description, ...(h.i18nKeys || []), h.code])]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge warn">producer</span>
              <span class="badge">${entry.count} call${entry.count === 1 ? '' : 's'}</span>
            </div>
            ${fileTitle(entry.file)}
            <ul class="calls">${hits}</ul>
          </article>`;
      }).join('');

      const consumers = DATA.baseNotificationConsumers.map((entry) => {
        const usages = entry.usages.map((u) =>
          `<li><span class="line">L${u.line}</span> · ${esc(u.code)}</li>`
        ).join('');
        const hay = [entry.file, entry.area, entry.kind, ...entry.usages.map((u) => u.code)]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge outline">${esc(entry.kind)}</span>
            </div>
            ${fileTitle(entry.file)}
            <ul class="calls">${usages}</ul>
          </article>`;
      }).join('');

      document.getElementById('bn-producers').innerHTML = producers || '<p class="empty">No producers found.</p>';
      document.getElementById('bn-consumers').innerHTML = consumers || '<p class="empty">No consumers found.</p>';
    }

    function renderMmds() {
      const entries = DATA.mmdsToasts || [];
      const cards = entries.map((entry) => {
        const hay = [
          entry.file,
          entry.area,
          entry.role,
          ...(entry.symbols || []),
          ...entry.calls.map((c) => `${c.hint} ${c.code}`),
        ]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge outline">${esc(entry.role)}</span>
              ${(entry.symbols || []).map((sym) =>
                `<span class="badge">${esc(sym)}</span>`
              ).join('')}
              <span class="badge">${entry.callCount} call${entry.callCount === 1 ? '' : 's'}</span>
            </div>
            ${fileTitle(entry.file)}
            ${callList(entry.calls)}
          </article>`;
      }).join('');

      document.getElementById('mmds-list').innerHTML = cards || '<p class="empty">No MMDS toast usages found.</p>';
      document.getElementById('mmds-count').textContent =
        `${entries.length} files · ${s.mmdsToastCalls ?? 0} calls`;
    }

    renderOverview();
    renderCl();
    renderBn();
    renderMmds();

    document.addEventListener('click', async (event) => {
      const btn = event.target.closest('.copy-btn');
      if (!btn) return;
      const text = btn.dataset.copy;
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text);
        btn.classList.add('copied');
        btn.innerHTML = CHECK_ICON;
        btn.setAttribute('aria-label', 'Copied');
        btn.title = 'Copied';
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = COPY_ICON;
          btn.setAttribute('aria-label', 'Copy path');
          btn.title = 'Copy path';
        }, 1500);
      } catch {
        btn.title = 'Copy failed';
      }
    });

    const search = document.getElementById('search');
    const searchWrap = document.querySelector('.search-wrap');
    function applyFilter() {
      const q = search.value.trim().toLowerCase();
      document.querySelectorAll('.card[data-hay]').forEach((card) => {
        card.classList.toggle('hidden', Boolean(q) && !card.dataset.hay.includes(q));
      });
    }
    search.addEventListener('input', applyFilter);

    function setTab(selected) {
      document.querySelectorAll('.tab').forEach((t) => {
        t.setAttribute('aria-selected', String(t.dataset.tab === selected));
      });
      document.querySelectorAll('[data-panel]').forEach((panel) => {
        panel.hidden = panel.dataset.panel !== selected;
      });
      if (searchWrap) {
        searchWrap.classList.toggle('is-hidden', selected === 'overview');
      }
      applyFilter();
    }

    document.querySelectorAll('.tab').forEach((tab) => {
      tab.addEventListener('click', () => setTab(tab.dataset.tab));
    });

    setTab('overview');

    window.addEventListener('keydown', (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === '/') {
        event.preventDefault();
        if (!searchWrap?.classList.contains('is-hidden')) {
          search.focus();
          search.select();
        }
      }
      if (event.key === 'Escape' && document.activeElement === search) {
        search.blur();
      }
    });
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "inventory.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dashboard" / "index.html",
    )
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text())
    html = TEMPLATE.replace("__DATA__", json.dumps(inventory))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
