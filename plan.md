# Plan – Minimal Interjection Feature for nbchat

## 1. Goal
Add a **real‑time interjection** capability that lets a user insert a message *mid‑stream* while the assistant is still reasoning or responding.  The user will use the **existing input box and Send button** – no new UI widgets.  The interjection is treated as a **normal user message** (no special roles, no tool calls).  The implementation must be thread‑safe and keep the architecture minimal.

## 2. Core Idea
1. The assistant’s response is streamed in a background `threading.Thread` (`self._stream_thread`).
2. When the user clicks **Send** during streaming, the current stream is **gracefully stopped**.
3. The user’s new message is appended to the conversation history **inside a lock**.
4. A **new streaming thread** is spawned that starts from the updated history.

This is effectively a *pause‑resume* pattern.

## 3. Thread Safety Strategy
* Use a single `threading.Lock` (`self._history_lock`) to guard:
  * `self.history` – the list of chat tuples.
  * `self._stream_thread` – the active streaming thread.
  * `_stop_streaming` flag – used to signal the current stream to stop.
* All accesses to these shared objects are wrapped with `with self._history_lock`.
* The UI callbacks (`_on_send`, `interject`) acquire the lock before checking the flag, setting it, and joining the thread.
* The streaming logic (`_process_conversation_turn`) releases the lock while it is waiting for the LLM, so the UI thread can still acquire it to stop the stream.

## 4. Minimal UI Changes
* No new buttons or widgets.
* The existing **Send** button will now perform the *interjection* logic when a stream is active.
* The **Stop** button remains for manual cancellation.

## 5. Updated `ChatUI` Design
### 5.1 New Instance Variable
```python
self._history_lock = threading.Lock()
```
### 5.2 Updated `_on_send`
```python
def _on_send(self, _):
    user_input = self.input_text.value.strip()
    if not user_input:
        return

    # Acquire lock before touching shared state
    with self._history_lock:
        # If a stream is running, stop it
        if self._stream_thread and self._stream_thread.is_alive():
            self._stop_streaming = True
            self._stream_thread.join()  # wait for the thread to exit

        # Append the new user message
        self.history.append(("user", user_input, "", "", ""))
        db.log_message(self.session_id, "user", user_input)

        # Clear the input box
        self.input_text.value = ""

        # Start a new streaming thread for the updated history
        self._stop_streaming = False
        self._stream_thread = threading.Thread(
            target=self._process_conversation_turn,
            daemon=True
        )
        self._stream_thread.start()
```
*All operations that modify `self.history`, the stop flag, or the thread are inside the lock.

### 5.3 Updated `_process_conversation_turn`
```python
def _process_conversation_turn(self):
    client = lazy_import("nbchat.core.client")
    tools  = lazy_import("nbchat.tools")
    db     = lazy_import("nbchat.core.db")

    # Build messages from the **current** history (no lock needed here – the history is already stable)
    messages = chat_builder.build_messages(self.history, self.system_prompt)
    for msg in messages:
        msg.pop("reasoning_content", None)

    for turn in range(self.MAX_TOOL_TURNS + 1):
        reasoning, content, tool_calls, finish_reason = self._stream_response(client, tools, messages)

        # ... (rest of the existing logic) ...
```
*Because the stream thread no longer needs to pause between tokens, it only checks the `_stop_streaming` flag in `_stream_response`.

### 5.4 Updated `_stream_response`
```python
for chunk in stream:
    if self._stop_streaming:
        stream.close()
        break
    # ... existing handling ...
```
*No additional locking is required here – the flag is read-only.

## 6. Edge‑Case Handling
| Situation | What happens | Notes |
|-----------|--------------|-------|
| User clicks **Send** while a stream is running | The stream is stopped, the new user message is appended, and a fresh stream starts | The user sees the new message appear immediately, and the assistant continues from there |
| User clicks **Send** multiple times quickly | Each click stops the current stream, starts a new one.  Because the lock serializes access, there is no race. | The assistant will process the messages in the order they were typed |
| Stream finishes naturally (no interjection) | Nothing special – the thread ends and `self._stop_streaming` stays `False` | `Send` can be pressed again to start a new turn |

## 7. Testing Plan
1. **Unit Test** – Mock the `client.chat.completions.create` to yield tokens.  Verify that pressing **Send** during streaming stops the first thread and starts a second one.
2. **Integration Test** – Run the full UI in a Jupyter notebook, type a question, let the assistant start responding, then type another message.  Confirm that the assistant’s next reply reflects the new message.
3. **Thread‑Safety Test** – Spin up 10 rapid **Send** actions and check that no exception occurs and the history is consistent.

## 8. Documentation
* Add a paragraph in the README under **Using the chat** explaining that you can type a new message while the assistant is still talking – the assistant will pause, incorporate your new input, and continue.

---

### Summary
* No supervisor or special roles.
* Minimal UI change – use existing Send button.
* Thread safety via a single lock.
* Clear start/stop of streaming threads.
* All new code resides in `ChatUI` and helper modules.

## 9. TODO List
The following table outlines the phases and the specific tasks that must be
completed to bring the feature to a working state.  Each task can be
assigned to a developer or tackled in a pair‑programming session.

| Phase | Task | Owner | Status |
|-------|------|-------|--------|
| **Design** | Review the current `ChatUI` implementation to confirm the
  locations where `self._stream_thread` and `self._stop_streaming` are
  used. | _Design Review_ | ☐ |
| **Threading** | Add `self._history_lock = threading.Lock()` in
  `__init__`. | _Implement_ | ☐ |
| **Send Button** | Modify `_on_send` to:
  1. Acquire the lock.
  2. Stop an existing stream if running.
  3. Append the new user message.
  4. Release the lock.
  5. Start a new stream thread. | _Implement_ | ☐ |
| **Stream Logic** | Update `_process_conversation_turn` so it does not
  rely on a global `self._stop_streaming` flag inside the loop.
  Ensure the flag is checked only in `_stream_response`. | _Implement_ | ☐ |
| **Interruption** | In `_stream_response`, add a check for
  `self._stop_streaming` after each chunk and break the loop.
  Close the stream properly. | _Implement_ | ☐ |
| **Lock Placement** | Verify that all accesses to `self.history`, the
  thread object, and the stop flag are guarded by the lock. | _Audit_ | ☐ |
| **Testing** | Write unit tests:
  * Mock the OpenAI client to produce a stream.
  * Simulate a user pressing Send while streaming.
  * Assert that the old thread terminates and the new thread starts.
  * Check that the final chat history contains both messages. | _Test_ | ☐ |
| **Integration** | Run the UI in a Jupyter notebook, type a prompt, wait for the assistant to start streaming, then type a new prompt and verify the assistant continues from the new context. | _Integration Test_ | ☐ |
| **Documentation** | Update the README and any relevant docs to
  explain the new interjection behaviour. | _Doc_ | ☐ |
| **Cleanup** | Remove any obsolete imports or dead code that
  was added during the refactor. | _Cleanup_ | ☐ |

### Deliverables
1. Updated `ChatUI` with thread‑safe interjection.
2. Updated unit and integration tests.
3. Updated documentation.
4. Commit with clear commit message: "Add minimal interjection feature with thread safety".
