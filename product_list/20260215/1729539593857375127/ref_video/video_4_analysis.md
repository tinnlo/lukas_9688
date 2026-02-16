# TikTok Ad Analysis Report | TikTok 广告分析报告

## Error | 错误
Gemini analysis failed.

```
Error during discovery for MCP server 'context7': MCP error -32001: Request timed outError during discovery for MCP server 'filesystem': MCP error -32001: Request timed outError during discovery for MCP server 'sequential-thinking': MCP error -32001: Request timed outHook registry initialized with 0 hook entries
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 1s.. Retrying after 1952.181215ms...
Attempt 2 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 2498.6079010000003ms...
Error executing tool read_file: Path not in workspace: Attempted path "/var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/tiktok_video_analysis/1729539593857375127/video_4/frames/frame_001.jpg" resolves outside the allowed workspace directories: /Users/lxt/Movies/TikTok/WZ/lukas_9688 or the project temp directory: /Users/lxt/.gemini/tmp/69dee1f720c9fcd70c6426abe817b72c553cd2ad675d17880db8f63507e16b7d
Error executing tool read_file: Path not in workspace: Attempted path "/var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/tiktok_video_analysis/1729539593857375127/video_4/frames/frame_002.jpg" resolves outside the allowed workspace directories: /Users/lxt/Movies/TikTok/WZ/lukas_9688 or the project temp directory: /Users/lxt/.gemini/tmp/69dee1f720c9fcd70c6426abe817b72c553cd2ad675d17880db8f63507e16b7d
Error executing tool read_file: Path not in workspace: Attempted path "/var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/tiktok_video_analysis/1729539593857375127/video_4/frames/frame_003.jpg" resolves outside the allowed workspace directories: /Users/lxt/Movies/TikTok/WZ/lukas_9688 or the project temp directory: /Users/lxt/.gemini/tmp/69dee1f720c9fcd70c6426abe817b72c553cd2ad675d17880db8f63507e16b7d
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 51.680491ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 1s.. Retrying after 1069.605494ms...
Attempt 2 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 2116.7190969999997ms...
Attempt 3 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Max attempts reached
Error when talking to Gemini API Full report available at: /var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/gemini-client-error-Turn.run-sendMessageStream-2026-02-15T20-11-32-561Z.json RetryableQuotaError: You have exhausted your capacity on this model. Your quota will reset after 2s.
    at classifyGoogleError (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:211:28)
    at retryWithBackoff (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:131:37)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async GeminiChat.makeApiCallAndProcessStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30)
    at async GeminiClient.processTurn (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:459:26)
    at async GeminiClient.sendMessageStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/client.js:559:20)
    at async file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/dist/src/nonInteractiveCli.js:193:34
    at async main (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/dist/src/gemini.js:492:9) {
  cause: {
    code: 429,
    message: 'You have exhausted your capacity on this model. Your quota will reset after 2s.',
    details: [ [Object], [Object] ]
  },
  retryDelayMs: 2467.394231
}
An unexpected critical error occurred:[object Object]
```
