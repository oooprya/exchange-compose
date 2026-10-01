#!/bin/bash

# Скрипт бэкапа и восстановления базы данных PostgreSQL
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="docker-compose.yml"

# Создаем папку для бэкапов, если её нет
mkdir -p $BACKUP_DIR

backup_database() {
    local backup_file="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"
    
    echo "📦 Создание бэкапа всей базы данных..."
    echo "   Файл: $backup_file"
    
    # Делаем дамп всей базы django_db со всеми таблицами
    docker-compose -f $COMPOSE_FILE exec -T db pg_dump -c -U django_user django_db | gzip > $backup_file
    
    echo "✅ Бэкап успешно создан!"
    echo "   Размер: $(du -h $backup_file | cut -f1)"
    
    # Показываем последние 5 бэкапов
    echo ""
    echo "📋 Список последних бэкапов:"
    ls -lh $BACKUP_DIR/backup_*.sql.gz | tail -5
}

restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo "❌ Ошибка: Укажите путь к файлу бэкапа."
        echo "   Пример: $0 restore backups/backup_xxxx.sql.gz"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        echo "❌ Ошибка: Файл не найден: $backup_file"
        return 1
    fi
    
    echo "⚠️  ВНИМАНИЕ: Это действие ПОЛНОСТЬЮ ПЕРЕЗАПИШЕТ текущую базу данных!"
    read -p "   Продолжить? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "❌ Восстановление отменено."
        return 1
    fi
    
    echo "🔄 Восстановление базы данных из бэкапа..."
    echo "   Файл: $backup_file"
    
    # Распаковываем и накатываем поток в контейнер
    gunzip -c $backup_file | docker-compose -f $COMPOSE_FILE exec -T db psql -U django_user django_db
    
    echo "✅ База данных успешно восстановлена!"
}

list_backups() {
    echo "📋 Доступные файлы бэкапов:"
    echo ""
    ls -lh $BACKUP_DIR/backup_*.sql.gz 2>/dev/null || echo "   Бэкапов не найдено"
}

# Маршрутизация команд без dev/prod
case "${1:-backup}" in
    backup)
        backup_database
        ;;
    restore)
        restore_database "$2"
        ;;
    list)
        list_backups
        ;;
    *)
        echo "Использование: $0 {backup|restore|list}"
        echo ""
        echo "Команды:"
        echo "  $0 backup             - Создать новый бэкап всей базы"
        echo "  $0 restore <файл>     - Восстановить базу из файла"
        echo "  $0 list                - Показать список бэкапов"
        echo ""
        echo "Примеры:"
        echo "  $0 backup"
        echo "  $0 restore backups/backup_20260604_081002.sql.gz"
        ;;
esac