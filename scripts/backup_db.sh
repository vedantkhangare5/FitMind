#!/bin/bash
set -e

# Configuration
DB_CONTAINER_NAME="fitmindai-backend-1"
DB_PATH="/data/fitmind.db"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/fitmind_backup_${DATE}.db"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

# Create backup dir if not exists
mkdir -p "$BACKUP_DIR"

echo "Starting SQLite backup at $DATE..."

# Execute SQLite online backup via the backend container to ensure consistency
# SQLite .backup command handles locking and WAL safely
docker exec -i "$DB_CONTAINER_NAME" sqlite3 "$DB_PATH" ".backup '/tmp/backup.db'"

# Copy the backup out of the container
docker cp "${DB_CONTAINER_NAME}:/tmp/backup.db" "$BACKUP_FILE"

# Clean up inside container
docker exec -i "$DB_CONTAINER_NAME" rm /tmp/backup.db

# Compress the backup
gzip "$BACKUP_FILE"

echo "Backup completed successfully: $COMPRESSED_FILE"

# Optional: Keep only last 7 days of backups
find "$BACKUP_DIR" -name "fitmind_backup_*.db.gz" -type f -mtime +7 -delete
echo "Cleaned up backups older than 7 days."
