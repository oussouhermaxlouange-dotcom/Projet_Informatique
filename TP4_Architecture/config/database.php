<?php
declare(strict_types=1);

use App\Support\Env;

/**
 * Configuration de la connexion, lue depuis .env.
 * Aucun identifiant réel n'est versionné : voir .env.example.
 */
return [
    'host' => Env::get('DB_HOST', '127.0.0.1'),
    'port' => Env::get('DB_PORT', '3306'),
    'base' => Env::get('DB_NAME', 'tp3_conventions'),
    'utilisateur' => Env::get('DB_USER', 'tp4_app'),
    'mot_de_passe' => Env::get('DB_PASSWORD', ''),
    'socket' => Env::get('DB_SOCKET', ''),
    'charset' => 'utf8mb4',
];
