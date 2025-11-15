# FastHTML Migration Guide

## Overview

This document explains the migration from the React/TypeScript/tRPC stack to FastHTML with Python.

## Technology Comparison

### Original Stack (React + tRPC)
- **Frontend**: React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Recharts
- **Backend**: Node.js 22, Express 4, tRPC 11, Drizzle ORM
- **Database**: MySQL/TiDB
- **Build Tools**: Vite 7, pnpm
- **Lines of Code**: ~2000+ (split across client/server)

### New Stack (FastHTML)
- **Framework**: FastHTML (Python)
- **Backend**: Starlette, Uvicorn (built into FastHTML)
- **Database**: PostgreSQL with SQLAlchemy
- **Lines of Code**: ~700 (single file)
- **Build Tools**: None required (Python only)

## Key Advantages of FastHTML

### 1. Simplicity
- Single language (Python) for entire stack
- No build process required
- Direct deployment: just run `python main.py`

### 2. Performance
- Server-side rendering = faster initial page load
- No JavaScript bundle to download
- Smaller total payload

### 3. Code Reduction
- ~65% less code (700 vs 2000+ lines)
- Single file vs multiple directories

## Preserved Features

✅ Same visual design - OKLCH color system maintained  
✅ Same database schema - Compatible structure  
✅ Same data source - Latvia open data API  
✅ Same functionality - Search, filters, analytics  
✅ Same user experience - Identical navigation and layout  
