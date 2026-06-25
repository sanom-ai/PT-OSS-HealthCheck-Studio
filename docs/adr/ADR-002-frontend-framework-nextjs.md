# ADR-002: Frontend framework

Status: Approved

## Context

The project requires a modern frontend framework for building a consultant workbench and report studio with good developer ergonomics, server-side rendering (SSR) for SEO where needed, fast page load, and type safety. The team prefers a React-based stack.

## Decision

Use Next.js (React) as the frontend framework for the PT-OSS HealthCheck Studio.

## Alternatives Considered

- Next.js (React): full-stack React framework with SSR/SSG, strong ecosystem, Vercel-friendly deployment.
- Remix: modern routing and form handling but smaller ecosystem.
- Vue/Nuxt: strong alternative if team prefers Vue, but current team familiarity favors React.

## Rationale

- Next.js supports SSR, SSG, API routes, and incremental static regeneration, which suit report pages and documentation needs.
- Large ecosystem and community; many deployment and monitoring integrations exist.
- Compatible with TypeScript for strong typing and developer DX.
- Plays well with Jamstack and containerised deployments; can be hosted on Vercel, Netlify, or standard CDN-backed containers.

## Consequences

Positive:
- Fast developer onboarding and rich UI ecosystem
- Good SEO and performance options for report pages
- Native TypeScript support and strong ecosystem

Trade-offs:
- Need to maintain a separate frontend repo or workspace if monorepo is not adopted; build pipeline complexity increases slightly.

Decision: Next.js (approved)
