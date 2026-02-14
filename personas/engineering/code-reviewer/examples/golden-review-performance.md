# Golden Example: Performance Issue in Hot Path

This example demonstrates reviewing code with a non-obvious performance
problem. The finding requires understanding both the code and the execution
context.

## Input: PR diff

```python
# api/routes/dashboard.py — Dashboard data aggregation

@app.route("/api/dashboard/<int:org_id>")
@require_auth
def get_dashboard(org_id: int):
    """Returns dashboard metrics for an organization."""
    org = Organization.query.get_or_404(org_id)

    # Get all team members
    members = User.query.filter_by(org_id=org_id).all()

    # Build activity feed
    activities = []
    for member in members:
        recent = Activity.query.filter_by(
            user_id=member.id
        ).order_by(
            Activity.created_at.desc()
        ).limit(10).all()
        activities.extend(recent)

    # Get project stats
    projects = Project.query.filter_by(org_id=org_id).all()
    project_stats = []
    for project in projects:
        task_count = Task.query.filter_by(project_id=project.id).count()
        done_count = Task.query.filter_by(
            project_id=project.id, status="done"
        ).count()
        project_stats.append({
            "name": project.name,
            "tasks": task_count,
            "completed": done_count,
            "progress": done_count / task_count if task_count > 0 else 0,
        })

    return jsonify({
        "org": org.name,
        "member_count": len(members),
        "activities": [a.to_dict() for a in sorted(
            activities, key=lambda a: a.created_at, reverse=True
        )[:20]],
        "projects": project_stats,
    })
```

## Expected Review Output

```markdown
## Code Review Summary

### Overview
Dashboard endpoint with two N+1 query patterns that will degrade linearly with
org size. Functional for small orgs but will cause visible latency for orgs with
50+ members or 20+ projects.

### Critical Issues
- **api/routes/dashboard.py:14-20** — N+1 query: one Activity query per member
  - Impact: An org with 200 members fires 201 queries (1 for members + 200 for
    activities). At 5ms per query, that's 1 second of database time. This is the
    dashboard — users hit it on every login.
  - Fix: Single query with join and window function:
    ```python
    from sqlalchemy import func

    # Get recent activities for all members in one query
    subq = db.session.query(
        Activity,
        func.row_number().over(
            partition_by=Activity.user_id,
            order_by=Activity.created_at.desc()
        ).label("rn")
    ).filter(
        Activity.user_id.in_([m.id for m in members])
    ).subquery()

    activities = db.session.query(Activity).select_entity_from(
        subq
    ).filter(subq.c.rn <= 10).all()
    ```

- **api/routes/dashboard.py:24-32** — N+1 query: two Task queries per project
  - Impact: An org with 30 projects fires 61 queries (1 for projects + 60 for
    task counts). Combined with the member N+1 above, a mid-size org generates
    260+ queries for a single page load.
  - Fix: Aggregate in one query:
    ```python
    from sqlalchemy import case

    project_stats = db.session.query(
        Project.name,
        func.count(Task.id).label("tasks"),
        func.count(case((Task.status == "done", 1))).label("completed"),
    ).outerjoin(Task).filter(
        Project.org_id == org_id
    ).group_by(Project.id).all()
    ```

### Suggestions
- **api/routes/dashboard.py:37-39** — Sorting in Python after fetching all activities
  - Recommendation: Move the sort and limit into the database query. The current
    approach fetches up to `members * 10` rows, sorts them in Python, then takes
    20. Let the DB do this work.

### Nits
(none — performance issues take priority over style)

### Security Considerations
- `@require_auth` is present — verify it also checks org membership (can user
  A see org B's dashboard?)

### What's Good
- Division-by-zero guard on progress calculation (`if task_count > 0`)
- Clean response structure with `.to_dict()` serialization
- Appropriate use of `get_or_404` for the org lookup

### Testing
- [ ] Unit tests cover new functionality
- [ ] Edge cases are tested (empty org, org with 0 projects)
- [ ] No test regressions
- [ ] **Missing:** Performance test or query count assertion for orgs > 50 members

**Verdict: request_changes** — N+1 queries will cause noticeable latency in
production. Fix with batch queries before merge.
```

## Why This Review Is Good

1. **Quantifies the impact** — "201 queries at 5ms each = 1 second" is better than "this might be slow"
2. **Explains the threshold** — "visible latency for orgs with 50+ members" tells the author when it matters
3. **Fixes are production-quality** — uses SQLAlchemy idioms the author is already using, not a different ORM
4. **Doesn't nitpick** — explicitly skips style nits because the perf issues are what matter
5. **Connects to user experience** — "this is the dashboard — users hit it on every login" explains why it's critical
