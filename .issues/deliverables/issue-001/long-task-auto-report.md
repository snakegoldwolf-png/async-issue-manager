# 🚀 Long Task Auto-Report - Be Proactive!

When you receive a task that will take significant time (>5 minutes), **automatically handle it without being asked**:

## Automatic Long Task Handling

**When you identify a long task:**

1. **Spawn a background session** to handle the work:
   ```
   sessions_spawn --task "Your task description" --label "task-name"
   ```

2. **Set a cron to check progress** (adjust timing based on task complexity):
   ```
   cron add --job '{
     "name": "Check task-name progress",
     "schedule": {"kind": "at", "at": "<ISO-timestamp-N-minutes-later>"},
     "payload": {"kind": "agentTurn", "message": "Check progress of task-name and report if complete"},
     "sessionTarget": "isolated",
     "delivery": {"mode": "announce", "channel": "feishu", "to": "bro"}
   }'
   ```

3. **When task completes** → Send completion notification:
   ```
   message send --channel feishu --target bro --message "✅ Task completed: [summary]"
   ```

4. **Clean up the cron** so it doesn't repeat:
   ```
   cron remove --jobId <job-id>
   ```

## What Counts as a Long Task?

- Learning and research (>10 min)
- Code implementation (>15 min)
- Multi-file refactoring
- System analysis or architecture design
- Data processing or migration
- Anything with multiple steps that takes >5 minutes

## Key Principles

- ✅ **Automatic detection** - You decide if it's a long task
- ✅ **Proactive execution** - Don't wait to be told to use background sessions
- ✅ **Completion notification** - Always report back when done
- ✅ **Clean up** - Remove cron jobs after completion
- ✅ **No manual tools** - This is built into your workflow, not a separate tool

## Example Flow

```
User: "Please analyze the codebase and write a refactoring plan"

You (internally):
1. This is a long task (>15 min)
2. Spawn background session with the analysis task
3. Set cron to check in 20 minutes
4. Reply: "Starting analysis in background, will notify when complete"

[20 minutes later, cron triggers]
5. Check if background session completed
6. If done: Send notification to bro with summary
7. Remove the cron job
```

## Important Notes

- **Don't ask permission** - Just do it for long tasks
- **Adjust timing** - 5 min tasks → check in 10 min, 30 min tasks → check in 45 min
- **One-shot crons** - Use "at" schedule, not "every" (no repeating)
- **Always clean up** - Remove cron after notification sent
- **Delivery config** - Use `"delivery": {"mode": "announce", "channel": "feishu", "to": "bro"}` for isolated sessions

---

**Last Updated**: 2026-02-25  
**Source**: @zohanlin's task auto-report mechanism  
**Implemented by**: Dev
