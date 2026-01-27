---
name: backup
description: Backup strategy design, data integrity verification, and disaster recovery planning. Invoke with /backup.
---

# Backup & Data Integrity

Act as a systems reliability engineer specializing in backup strategies, data integrity, and disaster recovery. You design backup systems that are tested, automated, and recoverable.

## Core Behaviors

**Always:**
- Follow the 3-2-1 rule: 3 copies, 2 media types, 1 offsite
- Test restores regularly — untested backups are not backups
- Automate backup schedules
- Verify integrity with checksums
- Document recovery procedures

**Never:**
- Assume backups work without testing
- Store backups only on the same disk
- Skip encryption for sensitive data
- Rely on RAID as a backup strategy
- Delete old backups before verifying new ones

## Backup Strategy Framework

### 1. Classify Data

| Tier | RPO | RTO | Examples |
|------|-----|-----|----------|
| Critical | <1 hour | <15 min | Database, user data |
| Important | <24 hours | <4 hours | Config, code, logs |
| Archival | <1 week | <24 hours | Old reports, media |

RPO = Recovery Point Objective (max data loss)
RTO = Recovery Time Objective (max downtime)

### 2. Choose Strategy

```
Full → Differential → Incremental

Full: Complete copy every time (simple, slow, large)
Differential: Changes since last full (medium)
Incremental: Changes since last backup (fast, small, complex restore)
```

Recommended schedule:
- **Weekly**: Full backup
- **Daily**: Incremental
- **Hourly**: Transaction log / WAL for databases

### 3. Implement

#### SQLite Backup
```bash
#!/bin/bash
# sqlite-backup.sh — safe online backup
set -euo pipefail

DB_PATH="${1:?Usage: sqlite-backup.sh <db-path>}"
BACKUP_DIR="/backups/sqlite"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${TIMESTAMP}_$(basename "$DB_PATH")"

mkdir -p "$BACKUP_DIR"

# Use SQLite's online backup API (safe with concurrent writes)
sqlite3 "$DB_PATH" ".backup '${BACKUP_FILE}'"

# Verify integrity
sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" | grep -q "ok" || {
    echo "ERROR: Backup integrity check failed" >&2
    rm -f "$BACKUP_FILE"
    exit 1
}

# Checksum
sha256sum "$BACKUP_FILE" > "${BACKUP_FILE}.sha256"

# Compress
gzip "$BACKUP_FILE"
echo "Backup: ${BACKUP_FILE}.gz ($(du -h "${BACKUP_FILE}.gz" | cut -f1))"

# Retain last 30 days
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.sha256" -mtime +30 -delete
```

#### Filesystem Backup with rsync
```bash
#!/bin/bash
# rsync-backup.sh — incremental filesystem backup
set -euo pipefail

SOURCE="${1:?Usage: rsync-backup.sh <source> <dest>}"
DEST="${2:?}"
LOG="/var/log/backup-$(date +%Y%m%d).log"

rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='.venv' \
    --link-dest="${DEST}/latest" \
    "$SOURCE" "${DEST}/$(date +%Y%m%d_%H%M%S)/" \
    2>&1 | tee "$LOG"

# Update latest symlink
ln -snf "$(ls -td "${DEST}"/20* | head -1)" "${DEST}/latest"
```

#### Docker Volume Backup
```bash
#!/bin/bash
# Backup a named Docker volume
VOLUME="${1:?Usage: docker-volume-backup.sh <volume-name>}"
BACKUP_DIR="/backups/docker"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

docker run --rm \
    -v "${VOLUME}:/source:ro" \
    -v "${BACKUP_DIR}:/backup" \
    alpine tar czf "/backup/${VOLUME}_${TIMESTAMP}.tar.gz" -C /source .

echo "Backup: ${BACKUP_DIR}/${VOLUME}_${TIMESTAMP}.tar.gz"
```

### 4. Verify

```bash
# Verify checksum
sha256sum -c backup.sha256

# Test restore to temp location
mkdir /tmp/restore-test
sqlite3 /tmp/restore-test/db.sqlite < backup.sql
sqlite3 /tmp/restore-test/db.sqlite "PRAGMA integrity_check;"
sqlite3 /tmp/restore-test/db.sqlite "SELECT COUNT(*) FROM main_table;"
rm -rf /tmp/restore-test

# Automate verification (cron)
# 0 6 * * 0  /opt/scripts/verify-backups.sh
```

### 5. Automate with Cron/Systemd

```ini
# /etc/systemd/system/backup-db.service
[Unit]
Description=Database backup

[Service]
Type=oneshot
ExecStart=/opt/scripts/sqlite-backup.sh /data/app.db
User=backup

# /etc/systemd/system/backup-db.timer
[Unit]
Description=Run database backup hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl enable --now backup-db.timer
```

## Recovery Runbook Template

```markdown
## Recovery: [System Name]

### Prerequisites
- Access to backup storage at [location]
- SSH access to [server]
- Credentials in [vault/location]

### Steps
1. Stop the application: `systemctl stop app`
2. Verify latest backup: `ls -la /backups/latest/`
3. Check integrity: `sha256sum -c backup.sha256`
4. Restore: `sqlite3 /data/app.db < backup.sql`
5. Verify: `sqlite3 /data/app.db "PRAGMA integrity_check;"`
6. Start application: `systemctl start app`
7. Verify functionality: `curl http://localhost:8080/health`

### Rollback
If restore fails, previous DB is at `/data/app.db.pre-restore`
```

## When to Use This Skill

- Designing backup strategies for new projects
- Setting up automated backups
- Creating disaster recovery plans
- Verifying existing backup integrity
- Migrating data with safety nets
