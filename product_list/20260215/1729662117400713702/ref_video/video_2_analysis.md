# TikTok Ad Analysis Report | TikTok 广告分析报告

## Error | 错误
Gemini analysis failed.

```
Hook registry initialized with 0 hook entries
Error executing tool list_allowed_directories: Tool execution denied by policy.
Error executing tool read_media_file: Tool execution denied by policy.
Error executing tool read_text_file: Tool execution denied by policy.
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 1s.. Retrying after 1813.504623ms...
Attempt 2 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 2670.0971369999997ms...
Attempt 1 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 2273.1916850000002ms...
Attempt 2 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Retrying after 2617.5781319999996ms...
Attempt 3 failed: You have exhausted your capacity on this model. Your quota will reset after 2s.. Max attempts reached
Error when talking to Gemini API Full report available at: /var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/gemini-client-error-Turn.run-sendMessageStream-2026-02-15T20-13-20-288Z.json RetryableQuotaError: You have exhausted your capacity on this model. Your quota will reset after 2s.
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
  retryDelayMs: 2738.92393
}
An unexpected critical error occurred:[object Object]
```
