#!/usr/bin/env python3
"""Build a static HTML dashboard from data/inventory.json."""

from __future__ import annotations

import argparse
import json
import subprocess
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
      --popover: oklch(0.205 0 0);
      --popover-foreground: oklch(0.985 0 0);
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

    .list-toolbar {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
      position: relative;
      z-index: 2;
    }

    .toolbar-filters {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .sort-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex: 0 0 auto;
    }

    .sort-label {
      font-size: 0.75rem;
      color: var(--muted-foreground);
      white-space: nowrap;
    }

    @media (max-width: 640px) {
      .toolbar-filters {
        width: 100%;
      }

      .sort-group {
        flex: 1 1 0;
        min-width: 0;
      }

      .sort-group .ui-select,
      .sort-group .ui-select-trigger {
        width: 100%;
        min-width: 0;
        max-width: none;
      }
    }

    .reset-btn {
      height: 2rem;
      padding: 0 0.75rem;
      border-radius: var(--radius);
      border: 1px solid var(--input);
      background: color-mix(in oklab, var(--input) 30%, transparent);
      color: var(--foreground);
      font: inherit;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
    }

    .reset-btn:hover {
      background: color-mix(in oklab, var(--muted) 50%, transparent);
    }

    .reset-btn:focus-visible {
      border-color: var(--ring);
      box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 50%, transparent);
    }

    .ui-select {
      position: relative;
    }

    .ui-select-trigger {
      display: inline-flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      height: 2rem;
      min-width: 9.5rem;
      max-width: 16rem;
      padding: 0 0.75rem;
      border-radius: var(--radius);
      border: 1px solid var(--input);
      background: color-mix(in oklab, var(--input) 30%, transparent);
      color: var(--foreground);
      font: inherit;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s, background-color 0.15s;
    }

    .ui-select-trigger:hover {
      background: color-mix(in oklab, var(--muted) 50%, transparent);
    }

    .ui-select-trigger:focus-visible,
    .ui-select[data-open] .ui-select-trigger {
      border-color: var(--ring);
      box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 50%, transparent);
    }

    .ui-select-value {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .ui-select-chevron {
      width: 1rem;
      height: 1rem;
      flex-shrink: 0;
      color: var(--muted-foreground);
    }

    .ui-select-content {
      position: absolute;
      top: calc(100% + 0.25rem);
      left: 0;
      z-index: 50;
      min-width: max(100%, 12rem);
      max-height: 16rem;
      overflow: auto;
      padding: 0.25rem;
      border-radius: calc(var(--radius) - 2px);
      border: 1px solid var(--border);
      background: var(--popover);
      color: var(--popover-foreground);
      box-shadow: 0 8px 24px oklch(0 0 0 / 40%);
    }

    .ui-select-item {
      position: relative;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-height: 2rem;
      padding: 0.25rem 1.75rem 0.25rem 0.5rem;
      border-radius: calc(var(--radius) - 4px);
      font-size: 0.8rem;
      line-height: 1;
      cursor: default;
      outline: none;
      user-select: none;
    }

    .ui-select-item:hover,
    .ui-select-item[data-highlighted="true"] {
      background: var(--muted);
    }

    .ui-select-check {
      position: absolute;
      right: 0.5rem;
      width: 0.875rem;
      height: 0.875rem;
      color: var(--foreground);
    }

    .ui-select-swatch {
      width: 0.5rem;
      height: 0.5rem;
      border-radius: 999px;
      flex-shrink: 0;
      background: var(--owner-color, var(--muted-foreground));
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

    .badge.owner {
      --owner-color: var(--foreground);
      background: color-mix(in oklab, var(--owner-color) 14%, transparent);
      border-color: color-mix(in oklab, var(--owner-color) 45%, transparent);
      color: var(--owner-color);
    }

    .card-title {
      margin: 0;
      display: flex;
      align-items: center;
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

    .card-title-actions {
      display: flex;
      align-items: center;
      flex-shrink: 0;
      gap: 0.375rem;
      padding-left: 0.625rem;
      border-left: 1px solid var(--border);
    }

    .copy-btn {
      flex-shrink: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      margin: 0;
      padding: 0;
      border: 1px solid var(--input);
      border-radius: 0.75rem;
      background: var(--muted);
      color: var(--foreground);
      text-decoration: none;
      cursor: pointer;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
    }

    .copy-btn:hover {
      background: #2b2b2b;
      border-color: #3c3c3c;
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
      width: 16px;
      height: 16px;
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
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

    .list-toolbar.is-hidden { display: none; }

    .status-wrap {
      overflow-x: auto;
    }

    .status-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8125rem;
    }

    .status-table th,
    .status-table td {
      padding: 0.75rem 0.85rem;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
      text-align: left;
    }

    .status-table th {
      font-size: 0.75rem;
      font-weight: 500;
      color: var(--muted-foreground);
      white-space: nowrap;
    }

    .status-table th:not(:first-child),
    .status-table td:not(:first-child) {
      text-align: right;
    }

    .status-owner {
      display: flex;
      align-items: center;
      min-height: 1.25rem;
    }

    .status-nums {
      font-variant-numeric: tabular-nums;
      font-weight: 500;
      color: var(--muted-foreground);
    }

    .status-pr {
      margin-top: 0.2rem;
      font-size: 0.75rem;
      color: var(--foreground);
    }

    .status-pr a {
      color: inherit;
      text-decoration: underline;
      text-underline-offset: 0.15em;
    }

    .status-pr a:hover {
      color: var(--teal-bright);
    }

    .status-pr a:focus-visible {
      outline: none;
      border-radius: 2px;
      box-shadow: 0 0 0 3px color-mix(in oklab, var(--ring) 50%, transparent);
    }

    .status-empty {
      color: var(--muted-foreground);
    }

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
      <button class="tab" role="tab" data-tab="status" aria-selected="true">Status</button>
      <button class="tab" role="tab" data-tab="cl" aria-selected="false">Component-library</button>
      <button class="tab" role="tab" data-tab="bn" aria-selected="false">BaseNotification</button>
      <button class="tab" role="tab" data-tab="mmds" aria-selected="false">MMDS</button>
      <button class="tab" role="tab" data-tab="overview" aria-selected="false">Overview</button>
    </div>

    <div class="list-toolbar">
      <div class="toolbar-filters">
        <div class="sort-group">
          <span class="sort-label" id="sort-label">Sort</span>
          <div class="ui-select" id="sort-select">
            <button type="button" class="ui-select-trigger" aria-haspopup="listbox" aria-expanded="false" aria-labelledby="sort-label">
              <span class="ui-select-value">Low → high</span>
              <svg class="ui-select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
            </button>
            <div class="ui-select-content" hidden role="listbox"></div>
          </div>
        </div>
        <div class="sort-group">
          <span class="sort-label" id="owner-label">Owner</span>
          <div class="ui-select" id="owner-select">
            <button type="button" class="ui-select-trigger" aria-haspopup="listbox" aria-expanded="false" aria-labelledby="owner-label">
              <span class="ui-select-value">All</span>
              <svg class="ui-select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
            </button>
            <div class="ui-select-content" hidden role="listbox"></div>
          </div>
        </div>
        <div class="sort-group">
          <span class="sort-label" id="pr-label">PR status</span>
          <div class="ui-select" id="pr-select">
            <button type="button" class="ui-select-trigger" aria-haspopup="listbox" aria-expanded="false" aria-labelledby="pr-label">
              <span class="ui-select-value">All</span>
              <svg class="ui-select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
            </button>
            <div class="ui-select-content" hidden role="listbox"></div>
          </div>
        </div>
        <button type="button" class="reset-btn" id="reset-filters">Reset</button>
      </div>
    </div>

    <hr class="separator" />

    <section id="panel-status" data-panel="status">
      <div class="status-wrap">
        <table class="status-table" id="status-table">
          <thead>
            <tr>
              <th>Team</th>
              <th>Component-library</th>
              <th>BaseNotification</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
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

    <section id="panel-overview" data-panel="overview" hidden>
      <div class="charts" id="overview-charts"></div>
    </section>
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
    const EXPORT_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6"/><path d="m10 14 11-11"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>`;

    function initSelect(root, { options, value = '', onChange } = {}) {
      if (!root) return null;
      const trigger = root.querySelector('.ui-select-trigger');
      const valueEl = root.querySelector('.ui-select-value');
      const content = root.querySelector('.ui-select-content');
      let items = options || [];
      let current = value;
      let highlighted = 0;

      function optionByValue(next) {
        return items.find((item) => item.value === next) || items[0];
      }

      function closeOthers() {
        document.querySelectorAll('.ui-select[data-open]').forEach((other) => {
          if (other === root) return;
          other.removeAttribute('data-open');
          other.querySelector('.ui-select-content')?.setAttribute('hidden', '');
          other.querySelector('.ui-select-trigger')?.setAttribute('aria-expanded', 'false');
        });
      }

      function renderItems() {
        content.innerHTML = items.map((item, index) => {
          const selected = item.value === current;
          const swatch = item.color
            ? `<span class="ui-select-swatch" style="--owner-color:${item.color}"></span>`
            : '';
          const check = selected
            ? CHECK_ICON.replace('aria-hidden="true"', 'class="ui-select-check" aria-hidden="true"')
            : '';
          return `<div class="ui-select-item" role="option" data-value="${esc(item.value)}" aria-selected="${selected}" data-highlighted="${index === highlighted}">${swatch}<span>${esc(item.label)}</span>${check}</div>`;
        }).join('');
        content.querySelector('[data-highlighted="true"]')?.scrollIntoView({ block: 'nearest' });
      }

      function syncTrigger() {
        const selected = optionByValue(current);
        valueEl.textContent = selected?.label ?? '';
        root.dataset.value = current;
      }

      function setValue(next, emit = false) {
        current = next;
        highlighted = Math.max(0, items.findIndex((item) => item.value === current));
        syncTrigger();
        renderItems();
        if (emit) onChange?.(current);
      }

      function open() {
        closeOthers();
        highlighted = Math.max(0, items.findIndex((item) => item.value === current));
        root.setAttribute('data-open', '');
        content.hidden = false;
        trigger.setAttribute('aria-expanded', 'true');
        renderItems();
      }

      function close() {
        root.removeAttribute('data-open');
        content.hidden = true;
        trigger.setAttribute('aria-expanded', 'false');
      }

      trigger.addEventListener('click', () => {
        if (root.hasAttribute('data-open')) close();
        else open();
      });

      content.addEventListener('pointerdown', (event) => {
        const item = event.target.closest('.ui-select-item');
        if (!item) return;
        event.preventDefault();
        setValue(item.dataset.value, true);
        close();
        trigger.focus();
      });

      trigger.addEventListener('keydown', (event) => {
        const openNow = root.hasAttribute('data-open');
        if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) {
          event.preventDefault();
          if (!openNow) {
            open();
            return;
          }
          if (event.key === 'ArrowDown') highlighted = Math.min(items.length - 1, highlighted + 1);
          if (event.key === 'ArrowUp') highlighted = Math.max(0, highlighted - 1);
          if (event.key === 'Enter' || event.key === ' ') {
            setValue(items[highlighted].value, true);
            close();
            return;
          }
          renderItems();
        }
        if (event.key === 'Escape' && openNow) {
          event.preventDefault();
          close();
        }
      });

      document.addEventListener('pointerdown', (event) => {
        if (!root.contains(event.target)) close();
      });

      syncTrigger();
      renderItems();
      content.hidden = true;

      return {
        getValue: () => current,
        setValue: (next) => setValue(next, false),
      };
    }

    function fileTitle(path, pr) {
      return `<h3 class="card-title">
        <span class="card-title-path">${esc(path)}</span>
        <span class="card-title-actions">
          ${prStatus(pr)}
          <button type="button" class="copy-btn" data-copy="${esc(path)}" aria-label="Copy path" title="Copy path">${COPY_ICON}</button>
        </span>
      </h3>`;
    }

    function ownerLabel(owner) {
      return String(owner).replace(/^@MetaMask\//, '').replace(/^metamask-/, '');
    }

    const OWNER_COLORS = {
      'accounts-engineers': 'oklch(0.78 0.10 250)',
      'card': 'oklch(0.80 0.12 75)',
      'confirmations': 'oklch(0.80 0.09 200)',
      'core-platform': 'oklch(0.76 0.08 260)',
      'delegation': 'oklch(0.76 0.10 310)',
      'design-system-engineers': 'oklch(0.80 0.10 190)',
      'earn': 'oklch(0.80 0.10 130)',
      'engagement': 'oklch(0.78 0.12 20)',
      'assets': 'oklch(0.78 0.11 145)',
      'mobile-admins': 'oklch(0.74 0.05 240)',
      'mobile-core-ux': 'oklch(0.80 0.10 230)',
      'mobile-platform': 'oklch(0.78 0.06 220)',
      'money-movement': 'oklch(0.80 0.11 160)',
      'perps': 'oklch(0.78 0.12 45)',
      'predict': 'oklch(0.78 0.13 300)',
      'product-safety': 'oklch(0.78 0.12 15)',
      'qa': 'oklch(0.78 0.08 120)',
      'rewards': 'oklch(0.82 0.13 95)',
      'social-ai': 'oklch(0.80 0.12 350)',
      'supply-chain': 'oklch(0.78 0.08 80)',
      'swaps-engineers': 'oklch(0.78 0.11 55)',
      'transactions': 'oklch(0.78 0.10 35)',
      'wallet-integrations': 'oklch(0.78 0.09 215)',
      'web3auth': 'oklch(0.76 0.13 280)',
    };
    const OWNER_PALETTE = Object.values(OWNER_COLORS);

    function ownerColor(label) {
      if (OWNER_COLORS[label]) return OWNER_COLORS[label];
      let hash = 0;
      for (let i = 0; i < label.length; i++) {
        hash = (hash * 33) ^ label.charCodeAt(i);
      }
      return OWNER_PALETTE[Math.abs(hash) % OWNER_PALETTE.length];
    }

    function ownerBadges(owners) {
      if (!owners?.length) {
        return '<span class="badge">unassigned</span>';
      }
      return owners.map((owner) => {
        const label = ownerLabel(owner);
        return `<span class="badge owner" style="--owner-color:${ownerColor(label)}" title="${esc(owner)}">${esc(label)}</span>`;
      }).join('');
    }

    function ownerAttr(owners) {
      if (!owners?.length) return 'unassigned';
      return owners.map(ownerLabel).join(' ');
    }

    function prStatus(pr) {
      if (!pr) return '';
      const label = pr.draft ? 'Open draft PR' : 'Open PR';
      const title = pr.title || (pr.number ? `PR #${pr.number}` : label);
      if (pr.url) {
        return `<a class="copy-btn" href="${esc(pr.url)}" target="_blank" rel="noreferrer" title="${esc(title)}" aria-label="${esc(label)}">${EXPORT_ICON}</a>`;
      }
      return `<span class="copy-btn" title="${esc(title)}" aria-label="${esc(label)}">${EXPORT_ICON}</span>`;
    }

    function prHay(pr) {
      if (!pr) return [];
      return [pr.draft ? 'draft pr' : 'open pr', String(pr.number || ''), pr.title || ''];
    }

    function prFilterValue(pr) {
      if (!pr) return 'none';
      return pr.draft ? 'draft' : 'open';
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

    function renderStatus() {
      function tally(entries, countOf) {
        const byOwner = new Map();
        for (const entry of entries || []) {
          const owners = entry.codeowners || [];
          const label = owners.length ? ownerLabel(owners[0]) : 'unassigned';
          let row = byOwner.get(label);
          if (!row) {
            row = { files: 0, calls: 0, prs: [], owner: owners[0] || '' };
            byOwner.set(label, row);
          }
          row.files += 1;
          row.calls += countOf(entry) || 0;
          if (entry.pr) {
            const key = entry.pr.number || entry.pr.url;
            if (key && !row.prs.some((p) => (p.number || p.url) === key)) {
              row.prs.push(entry.pr);
            }
          }
        }
        return byOwner;
      }

      const cl = tally(DATA.componentLibraryToasts, (e) => e.callCount);
      const bn = tally(
        [...(DATA.baseNotificationProducers || []), ...(DATA.baseNotificationConsumers || [])],
        (e) => e.count || e.usages?.length || 0,
      );
      const labels = [...new Set([...cl.keys(), ...bn.keys()])]
        .sort((a, b) => {
          if (a === 'unassigned') return 1;
          if (b === 'unassigned') return -1;
          return a.localeCompare(b);
        });

      function prLink(pr, label) {
        const title = pr.title || (pr.number ? `PR #${pr.number}` : label);
        if (!pr.url) return esc(label);
        return `<a href="${esc(pr.url)}" target="_blank" rel="noreferrer" title="${esc(title)}">${esc(label)}</a>`;
      }

      function cell(stats) {
        if (!stats?.files) return '<span class="status-empty">—</span>';
        const prs = [...(stats.prs || [])].sort((a, b) => (a.number || 0) - (b.number || 0));
        const pr = prs.length
          ? `<div class="status-pr">${prs.map((p) =>
              prLink(p, p.number ? `#${p.number}` : p.url || '')
            ).filter(Boolean).join(' · ')}</div>`
          : '';
        return `<div class="status-nums">${stats.calls} call${stats.calls === 1 ? '' : 's'}</div>${pr}`;
      }

      const body = labels.map((label) => {
        const ownerHtml = label === 'unassigned'
          ? ownerBadges([])
          : ownerBadges([cl.get(label)?.owner || bn.get(label)?.owner || label]);
        return `<tr>
          <th scope="row"><div class="status-owner">${ownerHtml}</div></th>
          <td>${cell(cl.get(label))}</td>
          <td>${cell(bn.get(label))}</td>
        </tr>`;
      }).join('');

      const tbody = document.querySelector('#status-table tbody');
      if (tbody) tbody.innerHTML = body || '<tr><td colspan="3" class="status-empty">No CODEOWNERS data.</td></tr>';
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

    const sortState = { cl: 'asc', bn: 'asc', mmds: 'asc' };

    function sortedByCalls(entries, dir, countOf) {
      return [...entries].sort((a, b) => {
        const diff = (countOf(a) || 0) - (countOf(b) || 0);
        if (diff !== 0) return dir === 'asc' ? diff : -diff;
        return String(a.file || '').localeCompare(String(b.file || ''));
      });
    }

    function renderCl() {
      const cards = sortedByCalls(DATA.componentLibraryToasts, sortState.cl, (e) => e.callCount).map((entry) => {
        const hay = [
          entry.file,
          entry.area,
          entry.role,
          entry.via,
          ...(entry.codeowners || []),
          ...(entry.codeowners || []).map(ownerLabel),
          ...prHay(entry.pr),
          ...entry.calls.map((c) => `${c.hint} ${c.code}`),
        ]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}" data-owners="${esc(ownerAttr(entry.codeowners))}" data-pr-status="${esc(prFilterValue(entry.pr))}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge">${entry.callCount} call${entry.callCount === 1 ? '' : 's'}</span>
              ${ownerBadges(entry.codeowners)}
            </div>
            ${fileTitle(entry.file, entry.pr)}
            ${callList(entry.calls)}
          </article>`;
      }).join('');

      document.getElementById('cl-list').innerHTML = cards || '<p class="empty">No matches.</p>';
      document.getElementById('cl-count').textContent =
        `${DATA.componentLibraryToasts.length} files · ${s.componentLibraryToastCalls} calls`;
    }

    function renderBn() {
      const producers = sortedByCalls(DATA.baseNotificationProducers, sortState.bn, (e) => e.count).map((entry) => {
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
        const hay = [
          entry.file,
          entry.area,
          ...(entry.codeowners || []),
          ...(entry.codeowners || []).map(ownerLabel),
          ...prHay(entry.pr),
          ...entry.hits.flatMap((h) => [h.title, h.description, ...(h.i18nKeys || []), h.code]),
        ]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}" data-owners="${esc(ownerAttr(entry.codeowners))}" data-pr-status="${esc(prFilterValue(entry.pr))}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge warn">producer</span>
              <span class="badge">${entry.count} call${entry.count === 1 ? '' : 's'}</span>
              ${ownerBadges(entry.codeowners)}
            </div>
            ${fileTitle(entry.file, entry.pr)}
            <ul class="calls">${hits}</ul>
          </article>`;
      }).join('');

      const consumers = sortedByCalls(DATA.baseNotificationConsumers, sortState.bn, (e) => e.usages?.length).map((entry) => {
        const usages = entry.usages.map((u) =>
          `<li><span class="line">L${u.line}</span> · ${esc(u.code)}</li>`
        ).join('');
        const hay = [
          entry.file,
          entry.area,
          entry.kind,
          ...(entry.codeowners || []),
          ...(entry.codeowners || []).map(ownerLabel),
          ...prHay(entry.pr),
          ...entry.usages.map((u) => u.code),
        ]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}" data-owners="${esc(ownerAttr(entry.codeowners))}" data-pr-status="${esc(prFilterValue(entry.pr))}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              <span class="badge outline">${esc(entry.kind)}</span>
              ${ownerBadges(entry.codeowners)}
            </div>
            ${fileTitle(entry.file, entry.pr)}
            <ul class="calls">${usages}</ul>
          </article>`;
      }).join('');

      document.getElementById('bn-producers').innerHTML = producers || '<p class="empty">No producers found.</p>';
      document.getElementById('bn-consumers').innerHTML = consumers || '<p class="empty">No consumers found.</p>';
    }

    function renderMmds() {
      const entries = sortedByCalls(DATA.mmdsToasts || [], sortState.mmds, (e) => e.callCount);
      const cards = entries.map((entry) => {
        const hay = [
          entry.file,
          entry.area,
          entry.role,
          ...(entry.symbols || []),
          ...prHay(entry.pr),
          ...entry.calls.map((c) => `${c.hint} ${c.code}`),
        ]
          .join(' ')
          .toLowerCase();
        return `
          <article class="card" data-hay="${esc(hay)}" data-owners="${esc(ownerAttr(entry.codeowners))}" data-pr-status="${esc(prFilterValue(entry.pr))}">
            <div class="badges">
              <span class="badge">${esc(entry.area)}</span>
              ${(entry.symbols || []).map((sym) =>
                `<span class="badge">${esc(sym)}</span>`
              ).join('')}
              <span class="badge">${entry.callCount} call${entry.callCount === 1 ? '' : 's'}</span>
            </div>
            ${fileTitle(entry.file, entry.pr)}
            ${callList(entry.calls)}
          </article>`;
      }).join('');

      document.getElementById('mmds-list').innerHTML = cards || '<p class="empty">No MMDS toast usages found.</p>';
      document.getElementById('mmds-count').textContent =
        `${entries.length} files · ${s.mmdsToastCalls ?? 0} calls`;
    }

    renderStatus();
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

    const listToolbar = document.querySelector('.list-toolbar');
    const separator = document.querySelector('.separator');

    function collectOwnerLabels() {
      const labels = new Set();
      let hasUnassigned = false;
      for (const list of [
        DATA.componentLibraryToasts,
        DATA.baseNotificationProducers,
        DATA.baseNotificationConsumers,
        DATA.mmdsToasts,
      ]) {
        for (const entry of list || []) {
          const owners = entry.codeowners || [];
          if (!owners.length) hasUnassigned = true;
          for (const owner of owners) labels.add(ownerLabel(owner));
        }
      }
      return {
        labels: [...labels].sort((a, b) => a.localeCompare(b)),
        hasUnassigned,
      };
    }

    const { labels: ownerLabels, hasUnassigned } = collectOwnerLabels();
    const ownerOptions = [
      { value: '', label: 'All' },
      ...ownerLabels.map((label) => ({ value: label, label, color: ownerColor(label) })),
      ...(hasUnassigned ? [{ value: 'unassigned', label: 'unassigned', color: 'var(--muted-foreground)' }] : []),
    ];

    const ownerSelect = initSelect(document.getElementById('owner-select'), {
      options: ownerOptions,
      value: '',
      onChange: () => applyFilter(),
    });

    const prSelect = initSelect(document.getElementById('pr-select'), {
      options: [
        { value: '', label: 'All' },
        { value: 'draft', label: 'draft' },
        { value: 'open', label: 'open' },
        { value: 'none', label: 'none' },
      ],
      value: '',
      onChange: () => applyFilter(),
    });

    function applyFilter() {
      const owner = ownerSelect?.getValue() || '';
      const prStatus = prSelect?.getValue() || '';
      document.querySelectorAll('.card[data-hay]').forEach((card) => {
        const owners = (card.dataset.owners || '').split(/\s+/).filter(Boolean);
        const ownerOk = !owner || owners.includes(owner);
        const prOk = !prStatus || card.dataset.prStatus === prStatus;
        card.classList.toggle('hidden', !(ownerOk && prOk));
      });
    }

    function applySort(dir) {
      const tab = document.querySelector('.tab[aria-selected="true"]')?.dataset.tab;
      if (!tab || tab === 'overview' || tab === 'status') return;
      sortState[tab] = dir;
      sortSelect?.setValue(dir);
      if (tab === 'cl') renderCl();
      else if (tab === 'bn') renderBn();
      else if (tab === 'mmds') renderMmds();
      applyFilter();
    }

    const sortSelect = initSelect(document.getElementById('sort-select'), {
      options: [
        { value: 'asc', label: 'Low → high' },
        { value: 'desc', label: 'High → low' },
      ],
      value: 'asc',
      onChange: applySort,
    });

    document.getElementById('reset-filters')?.addEventListener('click', () => {
      ownerSelect?.setValue('');
      prSelect?.setValue('');
      sortState.cl = 'asc';
      sortState.bn = 'asc';
      sortState.mmds = 'asc';
      const tab = document.querySelector('.tab[aria-selected="true"]')?.dataset.tab;
      if (tab && tab !== 'overview' && tab !== 'status') {
        applySort('asc');
        return;
      }
      sortSelect?.setValue('asc');
      applyFilter();
    });

    function setTab(selected) {
      document.querySelectorAll('.tab').forEach((t) => {
        t.setAttribute('aria-selected', String(t.dataset.tab === selected));
      });
      document.querySelectorAll('[data-panel]').forEach((panel) => {
        panel.hidden = panel.dataset.panel !== selected;
      });
      if (listToolbar) {
        listToolbar.classList.toggle('is-hidden', selected === 'overview' || selected === 'status');
      }
      if (separator) separator.hidden = selected === 'status';
      if (selected !== 'overview' && selected !== 'status') {
        sortSelect?.setValue(sortState[selected] || 'asc');
      }
      applyFilter();
    }

    document.querySelectorAll('.tab').forEach((tab) => {
      tab.addEventListener('click', () => setTab(tab.dataset.tab));
    });

    setTab('status');

    window.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        document.querySelectorAll('.ui-select[data-open]').forEach((root) => {
          root.removeAttribute('data-open');
          root.querySelector('.ui-select-content')?.setAttribute('hidden', '');
          root.querySelector('.ui-select-trigger')?.setAttribute('aria-expanded', 'false');
        });
      }
    });
  </script>
</body>
</html>
"""


def fetch_toast_prs(author: str = "amandaye0h", repo: str = "MetaMask/metamask-mobile") -> list[dict]:
    """Open toast-related PRs for the dashboard author."""
    try:
        raw = subprocess.check_output(
            [
                "gh",
                "pr",
                "list",
                "--repo",
                repo,
                "--author",
                author,
                "--state",
                "open",
                "--json",
                "number,title,isDraft,url,files",
                "--limit",
                "50",
            ],
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"Skipping PR status: {exc}")
        return []
    return [
        pr
        for pr in json.loads(raw)
        if "toast" in str(pr.get("title", "")).lower()
    ]


def attach_pr_status(inventory: dict, prs: list[dict]) -> None:
    """Attach open toast PRs onto matching inventory files."""
    by_file: dict[str, dict] = {}
    for pr in prs:
        info = {
            "number": pr["number"],
            "url": pr["url"],
            "title": pr["title"],
            "draft": bool(pr.get("isDraft")),
        }
        for file_info in pr.get("files") or []:
            path = file_info.get("path")
            if not path:
                continue
            existing = by_file.get(path)
            if existing is None or info["number"] > existing["number"]:
                by_file[path] = info

    attached = 0
    for key in (
        "componentLibraryToasts",
        "baseNotificationProducers",
        "baseNotificationConsumers",
        "mmdsToasts",
    ):
        for entry in inventory.get(key) or []:
            pr = by_file.get(entry.get("file"))
            if pr:
                entry["pr"] = pr
                attached += 1
            else:
                entry.pop("pr", None)
    print(f"Attached PR status to {attached} file(s) from {len(prs)} toast PR(s)")


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
    attach_pr_status(inventory, fetch_toast_prs())
    html = TEMPLATE.replace("__DATA__", json.dumps(inventory))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
