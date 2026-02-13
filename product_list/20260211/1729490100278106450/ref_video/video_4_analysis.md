# TikTok Ad Analysis Report | TikTok 广告分析报告

## Error | 错误
Gemini analysis failed.

```
Hook registry initialized with 0 hook entries
Attempt 1 failed with status 429. Retrying with backoff... GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3-flash-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3-flash-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/gaxios/build/src/gaxios.js:142:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async OAuth2Client.requestAsync (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/build/src/auth/oauth2client.js:429:18)
    at async CodeAssistServer.requestStreamingPost (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:171:21)
    at async CodeAssistServer.generateContentStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:29:27)
    at async file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/loggingContentGenerator.js:138:26
    at async retryWithBackoff (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:109:28)
    at async GeminiChat.makeApiCallAndProcessStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.28.0/gemini-3-flash-preview (darwin; x64) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/23.8.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    paramsSerializer: [Function: paramsSerializer],
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor]
  },
  response: {
    config: {
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      method: 'POST',
      params: [Object],
      headers: [Object],
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      paramsSerializer: [Function: paramsSerializer],
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor]
    },
    data: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3-flash-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    headers: {
      'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
      'content-length': '630',
      'content-type': 'application/json; charset=UTF-8',
      date: 'Wed, 11 Feb 2026 16:42:03 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=58',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '8c5f2f63e09fdb88',
      'x-content-type-options': 'nosniff',
      'x-frame-options': 'SAMEORIGIN',
      'x-xss-protection': '0'
    },
    status: 429,
    statusText: 'Too Many Requests',
    request: {
      responseURL: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse'
    }
  },
  error: undefined,
  status: 429,
  [Symbol(gaxios-gaxios-error)]: '6.7.1'
}
Attempt 2 failed with status 429. Retrying with backoff... GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3-flash-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3-flash-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/gaxios/build/src/gaxios.js:142:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async OAuth2Client.requestAsync (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/build/src/auth/oauth2client.js:429:18)
    at async CodeAssistServer.requestStreamingPost (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:171:21)
    at async CodeAssistServer.generateContentStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:29:27)
    at async file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/loggingContentGenerator.js:138:26
    at async retryWithBackoff (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:109:28)
    at async GeminiChat.makeApiCallAndProcessStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.28.0/gemini-3-flash-preview (darwin; x64) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/23.8.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    paramsSerializer: [Function: paramsSerializer],
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor]
  },
  response: {
    config: {
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      method: 'POST',
      params: [Object],
      headers: [Object],
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      paramsSerializer: [Function: paramsSerializer],
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor]
    },
    data: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3-flash-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    headers: {
      'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
      'content-length': '630',
      'content-type': 'application/json; charset=UTF-8',
      date: 'Wed, 11 Feb 2026 16:42:14 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=5425',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': 'd31f11e2951e8aa4',
      'x-content-type-options': 'nosniff',
      'x-frame-options': 'SAMEORIGIN',
      'x-xss-protection': '0'
    },
    status: 429,
    statusText: 'Too Many Requests',
    request: {
      responseURL: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse'
    }
  },
  error: undefined,
  status: 429,
  [Symbol(gaxios-gaxios-error)]: '6.7.1'
}
Error executing tool read_multiple_files: Tool execution denied by policy.
Attempt 1 failed with status 429. Retrying with backoff... GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3-flash-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3-flash-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/gaxios/build/src/gaxios.js:142:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async OAuth2Client.requestAsync (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/build/src/auth/oauth2client.js:429:18)
    at async CodeAssistServer.requestStreamingPost (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:171:21)
    at async CodeAssistServer.generateContentStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:29:27)
    at async file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/loggingContentGenerator.js:138:26
    at async retryWithBackoff (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:109:28)
    at async GeminiChat.makeApiCallAndProcessStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.28.0/gemini-3-flash-preview (darwin; x64) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/23.8.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    paramsSerializer: [Function: paramsSerializer],
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor]
  },
  response: {
    config: {
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      method: 'POST',
      params: [Object],
      headers: [Object],
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      paramsSerializer: [Function: paramsSerializer],
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor]
    },
    data: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3-flash-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    headers: {
      'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
      'content-length': '630',
      'content-type': 'application/json; charset=UTF-8',
      date: 'Wed, 11 Feb 2026 16:42:35 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=5524',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': 'd4a86d660d52580a',
      'x-content-type-options': 'nosniff',
      'x-frame-options': 'SAMEORIGIN',
      'x-xss-protection': '0'
    },
    status: 429,
    statusText: 'Too Many Requests',
    request: {
      responseURL: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse'
    }
  },
  error: undefined,
  status: 429,
  [Symbol(gaxios-gaxios-error)]: '6.7.1'
}
Attempt 2 failed with status 429. Retrying with backoff... GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3-flash-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3-flash-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/gaxios/build/src/gaxios.js:142:23)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async OAuth2Client.requestAsync (/Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/google-auth-library/build/src/auth/oauth2client.js:429:18)
    at async CodeAssistServer.requestStreamingPost (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:171:21)
    at async CodeAssistServer.generateContentStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:29:27)
    at async file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/loggingContentGenerator.js:138:26
    at async retryWithBackoff (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/retry.js:109:28)
    at async GeminiChat.makeApiCallAndProcessStream (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:431:32)
    at async GeminiChat.streamWithRetries (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/geminiChat.js:263:40)
    at async Turn.run (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/core/turn.js:66:30) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.28.0/gemini-3-flash-preview (darwin; x64) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/23.8.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    paramsSerializer: [Function: paramsSerializer],
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor]
  },
  response: {
    config: {
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      method: 'POST',
      params: [Object],
      headers: [Object],
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      paramsSerializer: [Function: paramsSerializer],
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor]
    },
    data: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3-flash-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    headers: {
      'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
      'content-length': '630',
      'content-type': 'application/json; charset=UTF-8',
      date: 'Wed, 11 Feb 2026 16:42:46 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=6398',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '2594e46ee6c74d46',
      'x-content-type-options': 'nosniff',
      'x-frame-options': 'SAMEORIGIN',
      'x-xss-protection': '0'
    },
    status: 429,
    statusText: 'Too Many Requests',
    request: {
      responseURL: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse'
    }
  },
  error: undefined,
  status: 429,
  [Symbol(gaxios-gaxios-error)]: '6.7.1'
}
Attempt 3 failed: No capacity available for model gemini-3-flash-preview on the server. Max attempts reached
Error when talking to Gemini API Full report available at: /var/folders/kt/j2l9r3892f1__8kc19n9dff00000gp/T/gemini-client-error-Turn.run-sendMessageStream-2026-02-11T16-42-54-944Z.json RetryableQuotaError: No capacity available for model gemini-3-flash-preview on the server
    at classifyGoogleError (file:///Users/lxt/.nvm/versions/node/v23.8.0/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/utils/googleQuotaErrors.js:242:16)
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
    message: 'No capacity available for model gemini-3-flash-preview on the server',
    details: [ [Object] ]
  },
  retryDelayMs: undefined
}
An unexpected critical error occurred:[object Object]
```
