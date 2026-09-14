# Handoff experience

The founder or a coordinating agent invokes a CLI. Success is a returned result
with evidence or a precise unfinished state that can be read from another
session. Keep operational details out of the founder's final Telegram answer.

| State | Observable behavior |
| --- | --- |
| Running | Job record exists with owner and deadline; the command waits. |
| Plain runner returned | Original stdout; record says returned, not task verified. |
| Structured completion | Summary and artifact references; full evidence in JSON record. |
| Blocked, refused or incomplete | Summary and pending reason; exit 4. |
| Invalid structured result | No raw answer presented as success; record says invalid_output. |
| Timeout or cancellation | Process group stopped; saved timed_out or cancelled state. |
| Lost process | Inspection marks an overdue/missing wrapper unconfirmed; no replay. |
| Repeated job ID | Saved result; different request rejected. |
| Cycle, depth or run limit | Delegation refused with a reason; caller resolves the task. |
| Profile drift | Dry run lists changed paths; no write. |
| Profile applied | Seven adapters updated after private backup. |
| Profile restore conflict | Later edits preserved; restore refused with the affected path. |

Do not optimize for the number of agents invoked. Optimize for a complete result
the next session can inspect. Run the synthetic README tests before release;
do not send a live Telegram message as an implicit test.
