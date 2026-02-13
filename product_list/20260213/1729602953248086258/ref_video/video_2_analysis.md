# TikTok Ad Analysis Report | TikTok 广告分析报告

## Error | 错误
Gemini analysis failed.

```
Hook registry initialized with 0 hook entries
Error executing tool list_allowed_directories: Tool execution denied by policy.
Error executing tool read_media_file: Tool execution denied by policy.
Error executing tool filesystem__list_directory: Tool execution denied by policy.
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 306.070121ms...
Error executing tool read_text_file: Tool execution denied by policy.
Error executing tool read_file: Path not in workspace: Attempted path "/var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/tiktok_video_analysis/1729602953248086258/video_2/frames/frame_001.jpg" resolves outside the allowed workspace directories: /Users/lxt/Movies/TikTok/WZ/lukas_9688 or the project temp directory: /Users/lxt/.gemini/tmp/69dee1f720c9fcd70c6426abe817b72c553cd2ad675d17880db8f63507e16b7d
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 991.437845ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 370.142649ms...
Error executing tool search_files: Tool execution denied by policy.
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 303.69831200000004ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 230.63771699999998ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 815.039188ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 539.6028210000001ms...
Attempt 2 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 2330.7943189999996ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 0s.. Retrying after 109.12832ms...
Attempt 2 failed: You have exhausted your capacity on this model. Your quota will reset after 1s.. Retrying after 1436.343836ms...
Attempt 3 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Max attempts reached
Error when talking to Gemini API Full report available at: /var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/gemini-client-error-Turn.run-sendMessageStream-2026-02-13T00-08-27-984Z.json RetryableQuotaError: You have exhausted your capacity on this model. Your quota will reset after 2s.
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
  retryDelayMs: 2127.076561
}
An unexpected critical error occurred:[object Object]
```
