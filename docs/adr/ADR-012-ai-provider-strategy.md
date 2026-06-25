# ADR-012: AI provider strategy

Status: Proposed

## Context

Platform will use LLMs for diagnostic interpretation, summarization, and report drafting. Provider choice affects cost, latency, and feature set.

## Decision

Design a pluggable AI provider adapter. Default to commercial LLM API (configurable per deployment). Support multiple providers via adapter pattern; include an offline/mock provider for local dev and tests.

## Rationale

- Adapter pattern prevents vendor lock-in and enables A/B testing
- Commercial providers provide higher quality and SLAs for production
- Local mock provider aids CI and deterministic tests

## Consequences

- Need to manage API keys securely in Vault/env
- Rate limits and cost must be architected into usage patterns

Decision: Pluggable AI provider adapters, commercial API default (approved)
