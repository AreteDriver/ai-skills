<!-- AUTO-GENERATED from registry.yaml — do not edit manually -->
<!-- Run: python3 scripts/generate-docs.py -->

# Persona Catalog

| Name | Category | Description | Schema |
|------|----------|-------------|--------|
| [api-tester](../../personas/api/api-tester/SKILL.md) | api | REST and GraphQL API testing — contract validation, load testing, regression suites, and endpoint verification |  |
| [database-ops](../../personas/api/database-ops/SKILL.md) | api | Database operations — schema design, migration authoring, query optimization, and SQL/ORM patterns |  |
| [oauth-integrator](../../personas/api/oauth-integrator/SKILL.md) | api | OAuth and API authentication — OAuth 2.0 flows, PKCE, token lifecycle, JWT validation, and provider integration |  |
| [webhook-designer](../../personas/api/webhook-designer/SKILL.md) | api | Webhook architecture — payload design, retry strategies, HMAC signature verification, and event-driven patterns |  |
| [plugin-builder](../../personas/claude-code/plugin-builder/SKILL.md) | claude-code | Builds Claude Code plugins — shareable packages that bundle skills, hooks, MCP server configs, and agent definitions into a single distributable unit with plugin.json manifest. Use when creating, scaffolding, packaging, or publishing Claude Code plugins. |  |
| [cicd-pipeline](../../personas/claude-code/cicd-pipeline/SKILL.md) | claude-code | Designs CI/CD pipelines that integrate Claude Code in headless mode for automated code review, test analysis, deployment gating, and PR triage. Use when building GitHub Actions workflows, GitLab CI pipelines, or any automation that uses Claude Code non-interactively via `claude -p` or the Agent SDK. |  |
| [session-memory-manager](../../personas/claude-code/session-memory-manager/SKILL.md) | claude-code | Manages Claude Code's persistent memory system — auto-memory files, cross-session context, project memory directories, and task handoff protocols. Use when organizing session memory, creating handoff documents, managing MEMORY.md files, or establishing continuity between Claude Code sessions. |  |
| [decision-log](../../personas/claude-code/decision-log/SKILL.md) | claude-code | Log high-leverage decisions from the current work session to the Arete Decision Log. Extracts architecture, UX, scope, tooling, and philosophy decisions. Invoke with /decision-log or /adl. |  |
| [prompt-library](../../personas/claude-code/prompt-library/SKILL.md) | claude-code | Extract effective prompts from the current session and save them to a reusable library. Captures prompts that worked well for future reference. Invoke with /prompt-library or /prompts. |  |
| [security-hooks](../../personas/claude-code/security-hooks/SKILL.md) | claude-code | Sets up Claude Code security hooks — protective PreToolUse guards that block sensitive file access, dangerous commands, destructive git ops, system path writes, network calls, and permission changes. Includes 7 ready-to-deploy hook scripts. |  |
| [hooks-designer](../../personas/claude-code/hooks-designer/SKILL.md) | claude-code | Designs Claude Code hooks — lifecycle event handlers (PreToolUse, PostToolUse) that enforce quality gates, block dangerous operations, auto-lint, run tests before commits, and log tool usage. Use when creating, debugging, or configuring Claude Code hooks for automated enforcement and workflow automation. |  |
| [mcp-server-builder](../../personas/claude-code/mcp-server-builder/SKILL.md) | claude-code | Builds and configures Model Context Protocol (MCP) servers — tools that extend Claude Code with custom capabilities like database access, API integrations, semantic search, and UI components. Use when creating MCP servers, configuring existing ones, debugging MCP connections, or designing tool interfaces for Claude. |  |
| [session-manager](../../personas/claude-code/session-manager/SKILL.md) | claude-code | Cross-session continuity for Claude Code — resume context, structured handoffs, session history tracking |  |
| [data-engineer](../../personas/data/data-engineer/SKILL.md) | data | Handles data collection, ingestion, cleaning, and pipeline design |  |
| [report-generator](../../personas/data/report-generator/SKILL.md) | data | Creates executive summaries, reports, and documentation of findings |  |
| [data-analyst](../../personas/data/data-analyst/SKILL.md) | data | Performs statistical analysis, finds patterns, and generates insights |  |
| [data-visualizer](../../personas/data/data-visualizer/SKILL.md) | data | Creates charts, dashboards, and visual representations of data |  |
| [release](../../personas/devops/release/SKILL.md) | devops | Create a new version release with proper tagging and changelog. Handles version bumping, tagging, and GitHub release creation. Invoke with /release [patch|minor|major] or just /release for patch. |  |
| [commit](../../personas/devops/commit/SKILL.md) | devops | Create well-formatted git commits with conventional commit style. Analyzes staged changes and generates appropriate commit messages. Invoke with /commit or after completing a task. |  |
| [backup](../../personas/devops/backup/SKILL.md) | devops | Backup strategy design, data integrity verification, and disaster recovery planning. Invoke with /backup. |  |
| [networking](../../personas/devops/networking/SKILL.md) | devops | Linux networking troubleshooting — DNS, firewalls, ports, routing, and connectivity diagnostics. Invoke with /networking. |  |
| [changelog](../../personas/devops/changelog/SKILL.md) | devops | Generate Changelog from Commits |  |
| [debug](../../personas/devops/debug/SKILL.md) | devops | Systematic Debugging Workflow |  |
| [deploy](../../personas/devops/deploy/SKILL.md) | devops | Deployment Checklist & Setup |  |
| [monitor](../../personas/devops/monitor/SKILL.md) | devops | Observability patterns for logging, metrics, alerting, and health checks in production systems. Invoke with /monitor. |  |
| [pre-release](../../personas/devops/pre-release/SKILL.md) | devops | Pre-Release Checklist |  |
| [process-management](../../personas/devops/process-management/SKILL.md) | devops | Monitor and control system processes with safety protections. Invoke with /process-management. |  |
| [ci](../../personas/devops/ci/SKILL.md) | devops | GitHub Actions Workflow Generator |  |
| [postmortem](../../personas/devops/postmortem/SKILL.md) | devops | Incident Postmortem Template |  |
| [systemd](../../personas/devops/systemd/SKILL.md) | devops | Systemd service management, unit files, timers, journalctl, and troubleshooting. Invoke with /systemd. |  |
| [lint](../../personas/devops/lint/SKILL.md) | devops | Run ruff linter and formatter. Checks code quality and auto-fixes issues. Invoke with /lint or /lint <path>. |  |
| [profile](../../personas/devops/profile/SKILL.md) | devops | Performance Profiling Guide |  |
| [test](../../personas/devops/test/SKILL.md) | devops | Run pytest with coverage summary. Provides quick feedback on test status and coverage. Invoke with /test or /test <path>. |  |
| [perf](../../personas/devops/perf/SKILL.md) | devops | Performance profiling and optimization for Python, Rust, and web applications. Invoke with /perf. |  |
| [pr](../../personas/devops/pr/SKILL.md) | devops | Pull Request Creator |  |
| [docker](../../personas/devops/docker/SKILL.md) | devops | Dockerfile Generator |  |
| [deps](../../personas/devops/deps/SKILL.md) | devops | Check for outdated dependencies and security vulnerabilities. Invoke with /deps. |  |
| [logs](../../personas/devops/logs/SKILL.md) | devops | Logging Setup & Analysis |  |
| [health](../../personas/devops/health/SKILL.md) | devops | Project Health Audit |  |
| [build](../../personas/devops/build/SKILL.md) | devops | Build and install the project in development mode. Handles venv creation and editable installs. Invoke with /build. |  |
| [package](../../personas/devops/package/SKILL.md) | devops | Release Packaging Checklist |  |
| [env](../../personas/devops/env/SKILL.md) | devops | Environment Management |  |
| [hauling-job-scheduler](../../personas/domain/hauling-job-scheduler/SKILL.md) | domain | Optimizes job scheduling, route planning, and capacity management for junk removal and hauling operations |  |
| [board-of-advisors](../../personas/domain/board-of-advisors/SKILL.md) | domain | USE WHEN the user is making a non-trivial decision (architecture, scope, positioning, hiring, kill-or-continue) and wants multi-perspective consultation rather than a single answer. Convenes four named advisors — Senior SE, Ops Sensei (TPS), Skeptic, Domain Expert — each speaks in turn, then a synthesis names where they agree, where they diverge, and the recommended call with the dissenting case preserved. Do NOT use for execution tasks, code changes, or yes/no questions with one right answer. Invoke with /board-of-advisors. |  |
| [arete-research-command-center](../../personas/domain/arete-research-command-center/SKILL.md) | domain | Multi-source intelligence workflow for Arete. Converts podcast/video/research batches into ranked actions for product, brand, funding, and agentic execution. |  |
| [eve-frontier-api](../../personas/domain/eve-frontier-api/SKILL.md) | domain | EVE Frontier World API integration — endpoints, auth (FusionAuth + Sui zkLogin), pagination, data normalization, and resilience patterns. Invoke with /eve-frontier-api. |  |
| [apple-dev-best-practices](../../personas/domain/apple-dev-best-practices/SKILL.md) | domain | Apple platform development best practices for Swift 6, SwiftUI, SwiftData, and iOS/macOS apps. Use when building any iOS or macOS app, writing Swift code, designing SwiftUI views, working with Xcode projects, implementing navigation, state management, concurrency, networking, persistence, or testing on Apple platforms. Triggers on Swift, SwiftUI, iOS, macOS, Xcode, UIKit, SwiftData, Core Data, XCTest, StoreKit, CloudKit, MapKit, HealthKit, or any Apple framework. Also use when reviewing Swift code, debugging iOS apps, migrating UIKit to SwiftUI, or planning Apple platform architecture. |  |
| [mentor-linux](../../personas/domain/mentor-linux/SKILL.md) | domain | Linux certification preparation mentor for RHCSA, Linux+, and LPIC-1 |  |
| [eve-frontier-chain](../../personas/domain/eve-frontier-chain/SKILL.md) | domain | EVE Frontier on-chain patterns — MUD v2 smart contracts, Sui SDK integration, smart assembly gating, and on-chain reputation systems. Invoke with /eve-frontier-chain. |  |
| [arete-funding-value-brief](../../personas/domain/arete-funding-value-brief/SKILL.md) | domain | Converts Arete execution signals into investor-grade funding narratives, milestone proofs, and de-risking plans. |  |
| [strategic-planner](../../personas/domain/strategic-planner/SKILL.md) | domain | Breaks down features into actionable implementation plans |  |
| [gamedev](../../personas/domain/gamedev/SKILL.md) | domain | Game development patterns for Bevy/Rust ECS, game loops, state machines, physics, and audio. Invoke with /gamedev. |  |
| [gameplay-tester](../../personas/domain/gameplay-tester/SKILL.md) | domain | Professional gameplay tester and QA analyst persona for playtesting, bug finding, UX assessment, balance evaluation, and player experience feedback. Use when evaluating game feel, finding bugs, assessing difficulty curves, or providing player-perspective feedback on games and interactive applications. |  |
| [tie-dye-business-coach](../../personas/domain/tie-dye-business-coach/SKILL.md) | domain | Socratic business coaching for handmade tie-dye businesses—diagnoses before prescribing, builds business intuition |  |
| [hauling-business-advisor](../../personas/domain/hauling-business-advisor/SKILL.md) | domain | Provides data-driven operational insights and recommendations for junk removal and hauling business optimization |  |
| [g13-layout](../../personas/domain/g13-layout/SKILL.md) | domain | Interactive G13 button position editor. Click on device image to set button coordinates. Invoke with /g13-layout. |  |
| [streamlit](../../personas/domain/streamlit/SKILL.md) | domain | Streamlit app patterns for layout, state management, data display, and deployment. Invoke with /streamlit. |  |
| [arete-studio-strategy-os](../../personas/domain/arete-studio-strategy-os/SKILL.md) | domain | Strategy and operating system persona for Arete. Converts intelligence into execution plans for workflow, process, AI strategy, and business growth. |  |
| [hauling-lead-qualifier](../../personas/domain/hauling-lead-qualifier/SKILL.md) | domain | Qualifies and prioritizes incoming leads for junk removal businesses based on job value, urgency, and conversion likelihood |  |
| [ogma](../../personas/domain/ogma/SKILL.md) | domain | Reverse-Engineering Synthesis Persona |  |
| [hauling-quote-generator](../../personas/domain/hauling-quote-generator/SKILL.md) | domain | Converts load estimates into professional customer-facing quotes with itemized pricing, fees, and terms for junk removal and hauling businesses |  |
| [eve-esi](../../personas/domain/eve-esi/SKILL.md) | domain | EVE Online ESI API integration patterns, authentication flows, rate limiting, and data modeling. Invoke with /eve-esi. |  |
| [hauling-image-estimator](../../personas/domain/hauling-image-estimator/SKILL.md) | domain | Analyzes photos of junk, debris, or estate contents to estimate volume, weight, item categories, and special disposal requirements for hauling/removal businesses |  |
| [eve-frontier-data](../../personas/domain/eve-frontier-data/SKILL.md) | domain | EVE Frontier data pipelines — killmail ingestion, smart assembly tracking, entity normalization, polling architecture, and SQLite/PostgreSQL storage patterns. Invoke with /eve-frontier-data. |  |
| [issue](../../personas/engineering/issue/SKILL.md) | engineering | GitHub Issue Creator |  |
| [review](../../personas/engineering/review/SKILL.md) | engineering | Code Review Checklist |  |
| [senior-software-analyst](../../personas/engineering/senior-software-analyst/SKILL.md) | engineering | Senior software analyst persona for codebase auditing, architecture mapping, documentation review, technical debt assessment, and system understanding. Use when you need to understand an unfamiliar codebase, evaluate architecture decisions, create documentation, or assess project health before making changes. |  |
| [code-builder](../../personas/engineering/code-builder/SKILL.md) | engineering | Writes clean, production-ready code based on plans |  |
| [software-architect](../../personas/engineering/software-architect/SKILL.md) | engineering | Designs system architecture and makes technical decisions | ✓ |
| [refactor](../../personas/engineering/refactor/SKILL.md) | engineering | Code Refactoring Analysis |  |
| [spec](../../personas/engineering/spec/SKILL.md) | engineering | Technical Specification Writer |  |
| [senior-software-engineer](../../personas/engineering/senior-software-engineer/SKILL.md) | engineering | Expert code reviewer, architect, and engineering mentor | ✓ |
| [types](../../personas/engineering/types/SKILL.md) | engineering | Python Type Hint Generator |  |
| [plan](../../personas/engineering/plan/SKILL.md) | engineering | Implementation Planning |  |
| [arch](../../personas/engineering/arch/SKILL.md) | engineering | Architecture Diagram Generator |  |
| [sql](../../personas/engineering/sql/SKILL.md) | engineering | SQL Query Optimization |  |
| [learn](../../personas/engineering/learn/SKILL.md) | engineering | Learning Resources & Path |  |
| [explain](../../personas/engineering/explain/SKILL.md) | engineering | Deep Code Explanation |  |
| [crud](../../personas/engineering/crud/SKILL.md) | engineering | CRUD Boilerplate Generator |  |
| [migrate](../../personas/engineering/migrate/SKILL.md) | engineering | Code Migration Helper |  |
| [code-reviewer](../../personas/engineering/code-reviewer/SKILL.md) | engineering | Reviews code for quality, security, and best practices | ✓ |
| [documentation-writer](../../personas/engineering/documentation-writer/SKILL.md) | engineering | Creates comprehensive documentation for code and systems |  |
| [estimate](../../personas/engineering/estimate/SKILL.md) | engineering | Task Estimation Techniques |  |
| [readme](../../personas/engineering/readme/SKILL.md) | engineering | README Generator |  |
| [mock](../../personas/engineering/mock/SKILL.md) | engineering | Test Mock & Fixture Generator |  |
| [seed](../../personas/engineering/seed/SKILL.md) | engineering | Test Data Generation |  |
| [testing-specialist](../../personas/engineering/testing-specialist/SKILL.md) | engineering | Creates comprehensive test suites for implementations | ✓ |
| [scaffold](../../personas/engineering/scaffold/SKILL.md) | engineering | Project Scaffolding |  |
| [api-docs](../../personas/engineering/api-docs/SKILL.md) | engineering | API Documentation Generator |  |
| [e2e](../../personas/engineering/e2e/SKILL.md) | engineering | End-to-End Test Setup |  |
| [composite-scorer](../../personas/engineering/composite-scorer/SKILL.md) | engineering | Weighted 0-100 composite scoring with category breakdowns, grade bands, and priority actions |  |
| [accessibility-checker](../../personas/security/accessibility-checker/SKILL.md) | security | Audits web applications for accessibility compliance — WCAG 2.2 AA/AAA conformance, ARIA patterns, keyboard navigation, screen reader support, color contrast, and semantic HTML. Use when reviewing UI code for accessibility, fixing a11y issues, or ensuring compliance with ADA/Section 508 requirements. |  |
| [security-sweep](../../personas/security/security-sweep/SKILL.md) | security | Fleet-wide security audit — runs /security-auditor across multiple repos, aggregates findings to FLEET-SECURITY.md, surfaces NEW findings since last sweep. Use for periodic fleet hardening, post-Dependabot-sweep verification, or before security-sensitive releases. |  |
| [security-auditor](../../personas/security/security-auditor/SKILL.md) | security | SAST + OWASP audit with LLM-triaged findings. Runs semgrep/bandit/gitleaks/pip-audit, filters false-positives, drafts remediation patches, persists SECURITY_FINDINGS.md with --diff for regression tracking. Use for security reviews, vuln scans, hardening, pre-pen-test prep. | ✓ |
| [a11y](../../personas/web/a11y/SKILL.md) | web | Accessibility Checklist |  |
| [headline-hook-generator](../../personas/web/headline-hook-generator/SKILL.md) | web | Generates scored headline variations, meta elements, and video hooks using proven conversion formulas |  |
| [web-performance](../../personas/web/web-performance/SKILL.md) | web | Optimizes website performance — Core Web Vitals, bundle analysis, image optimization, caching strategies, lazy loading, and Lighthouse score improvement. |  |
| [web-designer](../../personas/web/web-designer/SKILL.md) | web | Designs website layouts, color systems, typography, and visual hierarchy. Translates brand identity to Tailwind CSS design tokens and modern design systems. |  |
| [pixel-pick](../../personas/web/pixel-pick/SKILL.md) | web | Interactive coordinate picker - click on an image to get exact pixel coordinates. Useful for mapping UI element positions. Invoke with /pixel-pick <image-path>. |  |
| [seo-content-pipeline](../../personas/web/seo-content-pipeline/SKILL.md) | web | Orchestrates the full SEO content pipeline: research, write, optimize, scrub, publish with staged directories |  |
| [web-analytics](../../personas/web/web-analytics/SKILL.md) | web | Implements and interprets web analytics — GA4 setup, event tracking, conversion funnels, Google Search Console, UTM strategy, and A/B testing frameworks. |  |
| [web-content-writer](../../personas/web/web-content-writer/SKILL.md) | web | Writes website copy, blog posts, landing pages, and email content — SEO-aware, conversion-optimized, audience-targeted, and voice-consistent. |  |
| [web-frontend-builder](../../personas/web/web-frontend-builder/SKILL.md) | web | Builds production-grade frontend interfaces with React, Next.js, or static HTML/CSS. Component architecture, responsive design, and performance optimization. |  |
| [web-merchant](../../personas/web/web-merchant/SKILL.md) | web | Builds e-commerce functionality — product catalogs, shopping carts, Stripe/PayPal integration, order management, Shopify storefronts, and subscription billing. |  |
| [web-seo-optimizer](../../personas/web/web-seo-optimizer/SKILL.md) | web | Optimizes websites for search engines — technical SEO, structured data markup, Core Web Vitals, crawlability, sitemaps, and programmatic SEO patterns. |  |
| [align-debug](../../personas/web/align-debug/SKILL.md) | web | Overlay coordinate grid on screenshots for visual debugging. Helps align UI elements by showing pixel coordinates. Invoke with /align-debug <image-path>. |  |
| [content-scrubber](../../personas/web/content-scrubber/SKILL.md) | web | Detects and removes AI-generated patterns from content — em-dashes, filler phrases, robotic rhythm |  |
| [web-backend-builder](../../personas/web/web-backend-builder/SKILL.md) | web | Builds backend APIs and server logic with FastAPI, Flask, Express, or Next.js API routes. Database design, authentication, and API documentation. |  |
| [cro-analyst](../../personas/web/cro-analyst/SKILL.md) | web | Conversion rate optimization analysis with above-fold, CTA, trust signal, and cognitive load scoring |  |
| [brand-voice-architect](../../personas/web/brand-voice-architect/SKILL.md) | web | Defines and maintains brand voice context files that drive all content generation across channels |  |
| [web-deployer](../../personas/web/web-deployer/SKILL.md) | web | Deploys websites to Vercel, Fly.io, Netlify, Cloudflare, or VPS. DNS configuration, SSL certificates, CI/CD pipelines, and zero-downtime deployments. |  |
| [web-security-hardener](../../personas/web/web-security-hardener/SKILL.md) | web | Hardens websites against common attacks — security headers, CSP policies, input validation, CORS configuration, dependency auditing, and OWASP Top 10 mitigation. |  |
| [web-cms-manager](../../personas/web/web-cms-manager/SKILL.md) | web | Manages content management systems — WordPress themes/plugins, Ghost configuration, headless CMS integration (Sanity, Contentful, Strapi), and content modeling. |  |
| [compare](../../personas/web/compare/SKILL.md) | web | Side-by-side image comparison with difference highlighting. Useful for visual regression testing and UI changes. Invoke with /compare <image1> <image2>. |  |
