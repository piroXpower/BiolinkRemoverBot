<div align="center">

# 🛡️ BioLink Remover Bot

**An enterprise-grade, asynchronous Telegram group moderation suite engineered with Pyrogram v2 to automatically mitigate bio-link spam, enforce progressive warn limits, and maintain group integrity.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Pyrogram%20v2-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://docs.pyrogram.org/)
[![Engine](https://img.shields.io/badge/Crypto-TgCrypto-orange?style=for-the-badge)](https://github.com/pyrogram/tgcrypto)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[System Architecture](#-system-architecture) • [Key Capabilities](#-key-capabilities) • [Complete Source Code](#-complete-source-code) • [Deployment](#-deployment-guide) • [Command Reference](#-command-reference) • [Maintainer](#-maintainer--author)

---

</div>

## 📌 Executive Summary

**BioLink Protector Bot** targets a persistent evasive vector in Telegram group spam: malicious actors and botnets that bypass standard message text content filters by embedding promotional URLs, affiliate redirects, or phishing destinations directly within their **Telegram User Bio**.

When an unrestricted user posts a message inside a protected group, the bot asynchronously fetches their full profile, inspects the bio metadata using an aggressive regular-expression URL tokenizer, tracks progressive infractions on a per-chat basis, and executes automated administrative sanctions (**Mute** or **Ban**).

---

## ⚡ Key Capabilities

* **Sub-Millisecond Bio Inspection:** Intercepts message events and evaluates user profile bio payloads asynchronously without choking the MTProto event loop.
* **Comprehensive Regex Tokenizer:** Flags standard protocols (`http://`, `https://`), raw domains, generic TLDs (`.xyz`, `.top`, `.online`, `.app`, `.io`), and Telegram deep links (`t.me/*`).
* **Progressive Warn Engine:** Dynamic warning thresholds (1 to 5 warnings) per group with real-time state persistence.
* **Configurable Enforcement Modes:** Group admins can toggle punishment mode on-the-fly between temporary/permanent **Mute** (`ChatPermissions`) and permanent **Ban** (`ban_chat_member`).
* **Interactive Inline Admin Controls:** Callback query handlers attached directly to warning notifications allow administrators to forgive infractions or whitelist users with a single tap.
* **Zero-Downtime Hot-Reload (`/update`):** Self-updating mechanism utilizing Git hooks and in-process restart via `os.execl`.
* **Containerized Deployment:** Turnkey `Dockerfile` and `docker-compose.yml` specs with isolated volume bindings for state data.

---

## 🏗 System Architecture

```text
                           ┌───────────────────────────┐
                           │      Incoming Message     │
                           └─────────────┬─────────────┘
                                         │
                         [ Whitelisted / Admin Check ]
                                         │  (No)
                                         ▼
                           ┌───────────────────────────┐
                           │   Fetch Full Chat Bio     │
                           │     (app.get_chat)        │
                           └─────────────┬─────────────┘
                                         │
                            [ URL Regex Pattern Match ]
                                         │  (Match Found)
                                         ▼
                           ┌───────────────────────────┐
                           │  Increment Infraction     │
                           │      Count in State       │
                           └─────────────┬─────────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
        [ Count < Warn Limit ]                    [ Count >= Warn Limit ]
                    │                                         │
                    ▼                                         ▼
     ┌─────────────────────────────┐           ┌─────────────────────────────┐
     │ Dispatch Warn Message       │           │ Trigger Sanction            │
     │ with Inline Admin Callbacks │           │ (Restrict / Ban Member)     │
     └─────────────────────────────┘           └─────────────────────────────┘

```
<a id="key-capabilities"></a>
## ⚡ Key Capabilities

* **Sub-Millisecond Bio Inspection:** Asynchronously inspects message senders' full profiles and parses bio metadata without blocking MTProto event pipelines.
* **Aggressive URL Filtering:** Detects explicit protocols (`http://`, `https://`), standard/custom TLDs (`.xyz`, `.top`, `.online`, `.app`), and Telegram deep links (`t.me/*`).
* **Progressive Multi-Tier Warning System:** Configurable infraction limits (1–5) per group, retaining persistent violation counters.
* **Configurable Enforcement Policy:** Allows administrators to switch between temporary/indefinite **Mute** (`ChatPermissions`) and permanent **Ban** (`ban_chat_member`).
* **Interactive Inline Admin Actions:** Warning alerts include one-click inline buttons for resetting user warns or whitelisting trusted accounts instantly.
* **Zero-Downtime Hot-Reload:** Features an in-chat `/update` command that pulls changes from the Git remote and executes an in-memory process reload.
* **Containerized Ready:** Fully containerized setup supporting persistent JSON storage via Docker volumes.

---

<a id="deployment-guide"></a>
## 🚀 Deployment Guide

### Option 1: Native Host Process

```bash
# 1. Clone repository
git clone [https://github.com/yourusername/BiolinkRemoverBot.git](https://github.com/yourusername/BiolinkRemoverBot.git)
cd BiolinkRemoverBot

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
nano .env

# 5. Run the bot
python bot.py
    
