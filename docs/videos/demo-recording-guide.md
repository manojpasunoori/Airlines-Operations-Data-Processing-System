# AeroStream Demo Recording Guide

This guide defines a repeatable process for producing short, production-quality demo recordings for AeroStream.

## Purpose

Create consistent demo assets for:

- GitHub README previews
- Engineering documentation
- Internal architecture walkthroughs
- Release notes and stakeholder updates

## Recommended Recording Tools

| Tool | Platform | Best Use Case | Notes |
|---|---|---|---|
| ScreenToGif | Windows | Quick GIF capture for focused UI interactions | Lightweight and ideal for README GIFs |
| Loom | Windows / macOS / Linux (Web) | Narrated walkthrough videos with sharing links | Fast publishing and review workflow |
| OBS Studio | Windows / macOS / Linux | High-quality local recording for polished demos | Best for composited scenes and multiple sources |

## Demo Length and Format

| Asset Type | Recommended Length | Output Format | Recommended Resolution |
|---|---|---|---|
| README teaser video | 60–90 seconds | MP4 (H.264) | 1920x1080 |
| Feature GIF | 8–20 seconds | GIF (optimized) | 1280x720 |
| Full walkthrough | 3–6 minutes | MP4 (H.264) | 1920x1080 |

## Demo Storyboard (60–90 Seconds)

1. Start with platform startup status (`docker compose ps`) and service availability.
2. Show live ingestion by triggering simulator or posting sample event data.
3. Show Kafka-driven analytics updates in `streaming-analytics` logs and API output.
4. Open dashboard and highlight delay propagation + route reliability updates.
5. Close on observability view (Prometheus or Grafana) to prove runtime visibility.

## Features to Demonstrate

- Real-time flight ingestion from OpenSky-integrated flow
- Kafka event streaming through `flight-events`
- Delay propagation analysis in streaming analytics
- Route reliability metrics in APIs and dashboard
- Live SSE-driven dashboard updates
- Operational observability with Prometheus/Grafana

## Recording Preparation Checklist

- Ensure Docker services are healthy: `docker compose ps`
- Clear stale browser tabs and notifications
- Use a clean terminal theme with readable font size
- Set browser zoom to 100%
- Preload key URLs in separate tabs:
  - `http://localhost:8080`
  - `http://localhost:5173`
  - `http://localhost:9090`
  - `http://localhost:3000`

## Capture Workflow

1. Start recording and show project title/context briefly.
2. Trigger flight activity:
   - `curl -X POST http://localhost:8091/simulation/start`
3. Show live dashboard updates and key analytics panels.
4. Show one API verification request from gateway.
5. Stop recording and trim dead time at beginning/end.

## Export Recommendations

- Video codec: H.264
- Frame rate: 24 or 30 fps
- Bitrate: 4–8 Mbps for 1080p
- Audio: AAC (if narration is included)
- GIF optimization: limit colors and crop to active UI area

## File Naming Convention

Use descriptive, versioned names:

- `aerostream-demo-v1.mp4`
- `dashboard-live-updates-v1.gif`
- `delay-propagation-v1.gif`

Store finalized assets in:

- `docs/images/` for GIFs and screenshots
- `docs/videos/` for video links, notes, and publishing metadata

## Publishing Workflow

1. Upload MP4 to a host (YouTube, Loom, or organization-approved platform).
2. Replace README placeholder video link.
3. Replace placeholder images in `docs/images/` with final captures.
4. Verify Markdown rendering on GitHub in both light and dark themes.

## Quality Gate

Before publishing, confirm:

- The demo is under 90 seconds for README preview.
- Text and charts are readable at 100% zoom.
- No secrets, tokens, or local sensitive data are visible.
- Video and GIFs load correctly from repository-relative paths.
