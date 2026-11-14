---
name: creative-type-svg
description: Generate reference-guided black-on-white creative title lettering with Dreamina or LibTV and prepare Illustrator-editable SVGs for one title or a batch.
---

# Creative type to SVG

Use this skill when the user wants to create stylized title lettering from a reference image and turn the chosen black-and-white result into vector artwork.

## Codex and Kiro compatibility

Use this same folder in either application on macOS. Resolve resources relative to this SKILL.md, without machine-specific paths or bundled-runtime assumptions. Use the current host's shell tools and normal permissions.

- Codex: install under the configured CODEX_HOME skills directory, or `~/.codex/skills/creative-type-svg` by default. `agents/openai.yaml` provides optional Codex UI metadata.
- Kiro desktop: import the folder through Agent Steering & Skills → + → Import a skill → Local folder, or place it at `~/.kiro/skills/creative-type-svg` (workspace scope: `.kiro/skills/creative-type-svg`). Kiro uses SKILL.md directly.

## Inputs

Collect or infer:
- One local reference image (or several only when the user asks to use multiple references).
- Exact title text or an ordered list of titles, preserving punctuation and script. Accept a pasted list or a UTF-8 TXT (one title per line) / CSV with a `title` column. Preserve duplicate titles as separate numbered items unless the user asks to deduplicate; never silently split a single title on punctuation.
- Aspect ratio and resolution. If either is missing, ask before submitting a generation task.
- Optional number of variants; default to one unless the user asks for options.

## Fast mode (default)

Prioritize generation speed. Perform ordinary non-credit-consuming steps without asking for extra conversational permission, subject to host permissions. Before a Dreamina or LibTV submission, use the provider’s available cost estimate or explicit pricing response to determine the charge without submitting a paid task. When the provider confirms the total charge is exactly zero credits, proceed without a separate credit-approval question, including free retries or model changes. When the charge is greater than zero, tell the user the provider, model, image count and known total credits and obtain explicit authorization before submission. If the actual charge cannot be established, say that the cost is unknown and obtain authorization before submission; never assume it is zero. One approval covers the specified batch up to the disclosed total; a subsequent paid retry, quantity increase, cost increase, or provider/model change requires new authorization. Do not interpret a request to generate as consent to an undisclosed credit deduction. Never claim host permission prompts can be bypassed. Give a short start update and deliver files at completion; during long waits provide only necessary progress updates.


Reuse known CLI syntax, working login, and installed tracing tools. Check help only on first use, after an update, or after an unsupported-argument error. Do not routinely query credits or recheck the same dependencies for each title.

## Provider setup

Use the provider explicitly chosen by the user; if unspecified, use an available configured provider, asking only if the choice is ambiguous. Reuse the existing provider CLI, companion skill and login. This skill does not install Dreamina CLI. If the selected provider's CLI or integration is missing, explain what is missing and stop that provider workflow; do not silently switch providers. When login is needed, guide the user through the provider's normal browser authorization; never ask for passwords. Login and system permission dialogs still require the user's action where the application requires it.

Unless the user specifies a model, use Seedream 5.0 Lite for LibTV and Seedream 4.7 for Dreamina without asking the user to choose. An explicitly requested model overrides the relevant default. If the selected model or settings are unavailable, explain and ask before switching; do not silently substitute. Apply the credit authorization rule regardless of whether the model is default or user-selected.

For LibTV, use its installed official CLI and companion skill for model discovery, image reference, generation, status and download. Verify the selected model and requested settings are supported. Do not silently replace them. For Dreamina, use its installed CLI and companion instructions.

After setup, continue with the normal image-generation workflow below. Do not reinstall or relogin on later uses unless the executable or session is missing/invalid.

The user's base prompt is:

> 请你参考图中的字体风格设计标题文字：「{TITLE}」，纯白色背景，纯黑色字体。保持文字准确、完整、清晰可辨；只输出标题字样，不添加图案、装饰、阴影、渐变、边框或其他文字。

Keep the reference as a style guide; do not ask Dreamina to copy a font or logo exactly. Preserve the title exactly. Add only concise constraints needed for legibility and clean vector tracing.

## Generate with Dreamina

1. Use known CLI syntax; consult `dreamina -h` or `dreamina image2image -h` only when needed. Confirm that the local reference file exists and is readable.
2. Reuse the current login. If unauthenticated, follow the installed `dreamina-cli` skill's OAuth login procedure; never expose device codes in files or logs.
3. Generation consumes credits. Submit only when the user has asked to generate. Use `image2image` with the reference image, composed prompt, requested `--ratio`, and `--resolution_type`. Explicitly select Seedream 4.7 unless the user requests another model, using the installed CLI’s supported model identifier. Consult help for unknown or rejected values only.
4. Save the CLI output including `submit_id`. Use `--poll` only for a bounded wait. A task is complete only after `query_result` reports `gen_status=success`; then download with `--download_dir` (preview URLs are not download files). Do not duplicate an accepted task because polling failed.
5. Show the generated image and ask the user to choose a variant if multiple were requested. Do not trace every variant unless asked.

## Batch different titles in one style

A batch means multiple different titles, not multiple variants of one title. Default to one image and one SVG per title. Apply the same original reference, base prompt, ratio, resolution, model, and tracing settings to all items; change only the title unless requested. Do not use a preceding generated title as the next item's reference.

Apply the credit authorization rule above to the full batch. Zero-credit work proceeds without a credit-approval question; paid or unknown-cost work requires approval before submission. Ask only for missing settings or ambiguity that blocks submission. Check missing dependencies once before paid submissions.

Process items sequentially by default. Use numbered safe filenames and a separate output folder. Keep a minimal local `batch-manifest.json` for recovery: shared settings and each item's index, title, stage, accepted task ID and artifact paths. This is a local recovery record, not analytics. Save at submission and completion boundaries; do not add detailed logs or repeated status writes just for reporting.

Record `submitting` before the paid command and persist its returned ID immediately. If interrupted or the response is ambiguous, check available task history to recover the accepted ID; do not resubmit an uncertain submission. On resume, reuse accepted IDs and re-query them; retry downloads or local tracing without purchasing another image. Skip validated completed items. Retry terminally failed generation or poor lettering only with the user's authorization for another paid attempt; preserve prior attempts.

Inspect each image once for the exact requested text and suitable black-on-white outlines; reuse that inspection during conversion. Trace each single-variant item directly without asking the user to select between different titles. For multiple variants per title, request selection unless the user explicitly asked to export them all. Mark uncertain or incorrect text as `needs_review` and disclose it, rather than presenting it as correct. Continue independent items after isolated failures; stop further paid submissions for shared login, entitlement, or credit errors. Avoid per-item commentary; provide a brief update only during long waits or for actionable issues.

Deliver a ZIP of completed PNG/SVG pairs with the manifest and a concise success/failure list. Exclude credentials, OAuth output, virtual environments and unrelated files. If any items are unresolved, label the archive as partial and give a concrete resume instruction. Do not claim all titles succeeded merely because image generation finished.

## Make an editable SVG

For one requested result, proceed directly to SVG conversion. For multiple variants of the same title, wait for selection unless all were requested; different titles in a batch do not require selection. Create a vector trace suitable for Illustrator:

- Reuse the raster inspection already performed, or inspect once if not yet checked. Confirm the background is white and lettering is black; remove/ignore small stray marks, normalize to a clean binary silhouette, and retain counters/holes inside glyphs.
- Prefer a locally available bitmap tracer such as `vtracer` or Potrace. Check availability before choosing a method. For Potrace, make a high-contrast bitmap and export SVG; for VTracer, use the Python API `convert_image_to_svg_py` with `colormode="binary"` and `mode="spline"`; do not assume a `python -m vtracer` command exists. Do not assume either tool is installed.
- If no tracer is available, explain the Pillow and VTracer dependency and install them in a dedicated virtual environment with an available Python 3 (`python3 -m venv <writable-cache>/creative-type-svg-venv`, then that environment's `python -m pip install Pillow vtracer`), using the host's normal permissions. Reuse this environment later. If Python is absent or installation fails, report the blocker and retain the PNG for Illustrator Image Trace. Do not produce a fake SVG that merely embeds the raster image and call it vectorized.
- Keep the original generated raster. Save the SVG beside it with a clear filename. Ensure SVG paths are black, background is transparent or white as requested, viewBox is tight, and compound paths preserve counters. Validate once that SVG XML parses and contains actual vector paths, not an embedded bitmap. Extra render previews and repeated visual checks are optional when a visible problem needs investigation.
- Mention that traced paths are editable vector shapes, not a font file; complex outlines may need manual cleanup in Illustrator.

## Output

Provide the generated raster, selected SVG, and a short note on path quality or any limitations. Keep settings and task IDs in the local recovery record or CLI output; do not repeat them in the final message unless requested. Never claim SVG conversion succeeded unless the output contains actual vector paths and has been validated.
