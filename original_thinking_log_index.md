# Single-agent run records

The benchmark contains 18 runs: six agent configurations under each of three
prompt conditions. Each run directory contains two standardized records:

- `original_visible_thinking_log.md`: visible saved messages and tool events in
  chronological order;
- `original_visible_session_events.jsonl`: the corresponding machine-readable
  event sequence.

The formatted `thinking_log.tex` and `thinking_log.pdf` files are
author-prepared chronological accounts used in the paper. They organize the
recorded hypotheses, commands, results, counterexamples, and final claims.

These records describe saved, visible interactions. Opaque or encrypted private
reasoning was not reconstructed.

## Coverage

| Condition | Configuration | Visible record | Rewritten record |
| --- | --- | --- | --- |
| false hint | Claude Opus 4.8 max | [Markdown](case_1/claude_opus_48_max/original_visible_thinking_log.md) | [PDF](case_1/claude_opus_48_max/thinking_log.pdf) |
| false hint | Claude Opus 4.8 ultra | [Markdown](case_1/claude_opus_48_ultra/original_visible_thinking_log.md) | [PDF](case_1/claude_opus_48_ultra/thinking_log.pdf) |
| false hint | Codex 5.4 xhigh | [Markdown](case_1/codex_54_xhigh/original_visible_thinking_log.md) | [PDF](case_1/codex_54_xhigh/thinking_log.pdf) |
| false hint | Codex 5.5 xhigh | [Markdown](case_1/codex_55_xhigh/original_visible_thinking_log.md) | [PDF](case_1/codex_55_xhigh/thinking_log.pdf) |
| false hint | DeepSeek v4 pro | [Markdown](case_1/deepseek_v4_pro/original_visible_thinking_log.md) | [PDF](case_1/deepseek_v4_pro/thinking_log.pdf) |
| false hint | Fugu ultra | [Markdown](case_1/fugu_ultra/original_visible_thinking_log.md) | [PDF](case_1/fugu_ultra/thinking_log.pdf) |
| true hint | Claude Opus 4.8 max | [Markdown](case_2/claude_opus_48_max/original_visible_thinking_log.md) | [PDF](case_2/claude_opus_48_max/thinking_log.pdf) |
| true hint | Claude Opus 4.8 ultra | [Markdown](case_2/claude_opus_48_ultra/original_visible_thinking_log.md) | [PDF](case_2/claude_opus_48_ultra/thinking_log.pdf) |
| true hint | Codex 5.4 xhigh | [Markdown](case_2/codex_54_xhigh/original_visible_thinking_log.md) | [PDF](case_2/codex_54_xhigh/thinking_log.pdf) |
| true hint | Codex 5.5 xhigh | [Markdown](case_2/codex_55_xhigh/original_visible_thinking_log.md) | [PDF](case_2/codex_55_xhigh/thinking_log.pdf) |
| true hint | DeepSeek v4 pro | [Markdown](case_2/deepseek_v4_pro/original_visible_thinking_log.md) | [PDF](case_2/deepseek_v4_pro/thinking_log.pdf) |
| true hint | Fugu ultra | [Markdown](case_2/fugu_ultra/original_visible_thinking_log.md) | [PDF](case_2/fugu_ultra/thinking_log.pdf) |
| no hint | Claude Opus 4.8 max | [Markdown](case_3/claude_opus_48_max/original_visible_thinking_log.md) | [PDF](case_3/claude_opus_48_max/thinking_log.pdf) |
| no hint | Claude Opus 4.8 ultra | [Markdown](case_3/claude_opus_48_ultra/original_visible_thinking_log.md) | [PDF](case_3/claude_opus_48_ultra/thinking_log.pdf) |
| no hint | Codex 5.4 xhigh | [Markdown](case_3/codex_54_xhigh/original_visible_thinking_log.md) | [PDF](case_3/codex_54_xhigh/thinking_log.pdf) |
| no hint | Codex 5.5 xhigh | [Markdown](case_3/codex_55_xhigh/original_visible_thinking_log.md) | [PDF](case_3/codex_55_xhigh/thinking_log.pdf) |
| no hint | DeepSeek v4 pro | [Markdown](case_3/deepseek_v4_pro/original_visible_thinking_log.md) | [PDF](case_3/deepseek_v4_pro/thinking_log.pdf) |
| no hint | Fugu ultra | [Markdown](case_3/fugu_ultra/original_visible_thinking_log.md) | [PDF](case_3/fugu_ultra/thinking_log.pdf) |

For the outcome labels, test counts, and post-run corrections, see
[`paper/baseline_run_manifest.md`](paper/baseline_run_manifest.md).
