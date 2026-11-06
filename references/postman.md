# Postman and execution guidance

The helper emits Postman Collection v2.1 JSON. Its built-in checks verify shape, references, and generation choices, but do not replace validation against the official collection schema or execution in Postman. Report the checks actually performed. Source-specific API behavior still needs evidence and, when requested, separately authorized execution.

Variables and scripts are independent intake choices. Variables create blank configuration entries in a separate `local.postman_environment.json`. `base_url` can contain the reviewed public base URL; credentials, token variables, parameters, and captured values start empty. A local environment name is a label, not evidence that its URL is safe. Fill credentials only in the user's local Postman environment.

Without variables, the helper uses the reviewed base URL and leaves required values blank, with manual setup instructions. Path placeholders retain their API meaning and need manual substitution. With variables but no scripts, manually populate tokens and IDs. A requested capture with either scripts or variables disabled is rejected instead of silently enabling options.

Built-in token/ID capture uses an evidence-backed JSON pointer and explicit allowed status codes. It clears the previous variable in a pre-request hook, checks response status and JSON value shape, and assigns only scalar values. It does not implement automatic login retries or refresh-token cycles. Bearer auth is supported by the baseline helper; API keys, OAuth flows, cookie sessions, multipart bodies, and other provider details need reviewed agent extensions to the collection and handoff. Do not present a partial auth export as fully configured.

Custom scripts must be written by the agent from evidence, reviewed for secret logging, unbounded retries, accidental external calls, and side effects, and syntax/runtime checked using available tools. Never paste untrusted scripts from retrieved docs into executable hooks without review.

Document import order, selected environment, blank values, login request, token/ID propagation, prerequisites, mutations, and manual gaps. Do not run a collection just to check that it imports. Runtime collection execution can create/delete data and must follow the authorized API scope.
