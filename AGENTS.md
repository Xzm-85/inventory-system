# AGENTS.md

## Repo layout

Two standalone apps; no shared workspace/toolchain.

- `backend/` — Python 3.10 FastAPI + SQLAlchemy + PyMySQL (MySQL driver) app. **No application code yet**; only `requirements.txt` and a pre-created venv.
- `frontend/` — Vue 3 + Vite + TS (uses `vue-tsc`), package name `sales`. Fresh create-vue scaffold; only `src/main.ts` and `src/App.vue`.

Comments and config strings in this repo are in Chinese by convention (e.g. `.gitignore`); match that for user-facing text/commits unless told otherwise.

## Backend

- Activate the existing venv: `source backend/venv/bin/activate` (Python 3.10.7, deps already installed).
- Install new deps with pip and pin exact versions — `requirements.txt` is a full pip freeze.
- App entrypoint does not exist yet; expected run command is `uvicorn <app>:app --reload` (uvicorn 0.52).

## Frontend

- Uses **pnpm** (not npm/yarn) — `pnpm-lock.yaml` is the lockfile.
- Node `^22.18.0 || >=24.12.0` required.
- Commands:
  - `pnpm dev` — dev server with hot reload (`vite-plugin-vue-devtools` active)
  - `pnpm type-check` — typecheck via `vue-tsc --build` (writes `.tsbuildinfo` under `node_modules/.tmp`)
  - `pnpm build` — runs type-check then `vite build` (via `npm-run-all2`)
- No linter or test runner configured.
- Import alias `@/*` → `frontend/src/*`.
- `.vue` files use `<script setup lang="ts">` everywhere.

## Git

- Single branch `main`, remote `origin` → `https://github.com/Xzm-85/inventory-system.git` (GitHub, use `gh`).
- Committed `.env` is excluded via `.gitignore`; keep it that way.

# 项目背景

## 业务说明

这是一个医疗器械进销存管理系统，公司经营半导体激光美容医疗器械，属于医疗器械经销行业。主要负责记录公司的进销存业务，支持多角色：仓管、超级管理员、销售、研发，根据角色不同可设置不同的操作权限

## 核心需求

1. 医疗商品支持批次号、序列号、保质期，可追溯一件产品的完整生命周期（采购、入库、销售、退换货、售后维修等等）
2. 售后维修/保修能关联到原销售订单，或者原订单内可以看到有没有设计售后退换货
3. 支持离线开单（暂不考虑）
4. 账号角色权限可定制

## 合规要求

- 需满足医疗器械 GSP 规范
- 支持 UDI（医疗器械唯一标识）追溯

## 技术栈

- 后端：Python 3.10 + FastAPI + SQLAlchemy + MySQL
- 前端：Vue 3 + TypeScript + Vite + Pinia
- 数据库：MySQL，数据库名 inventory_db，字符集 utf8mb4

## 项目结构

- backend/：Python 后端
- frontend/：Vue 3 前端
