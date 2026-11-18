<?php
declare(strict_types=1);

use App\Repositories\Database;
use App\Support\Env;

require dirname(__DIR__) . '/src/autoload.php';
Env::load(dirname(__DIR__) . '/.env');

echo "Test de connexion PDO\n";
echo "---------------------\n";

try {
    $pdo = Database::connexion();

    $version = (string) $pdo->query('SELECT VERSION()')->fetchColumn();
    $base = (string) $pdo->query('SELECT DATABASE()')->fetchColumn();
    $pilote = (string) $pdo->getAttribute(PDO::ATTR_DRIVER_NAME);

    echo "OK  connexion établie\n";
    echo "    serveur : {$version}\n";
    echo "    base    : {$base}\n";
    echo "    pilote  : {$pilote}\n";
    exit(0);
} catch (Throwable $exception) {
    fwrite(STDERR, "ECHEC  " . $exception->getMessage() . "\n");
    fwrite(STDERR, "Vérifier .env (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD ou DB_SOCKET).\n");
    exit(1);
}
