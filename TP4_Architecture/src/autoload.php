<?php
declare(strict_types=1);

/**
 * Autoload PSR-4 minimal, sans Composer.
 * Le préfixe App\ correspond au dossier src/.
 */
spl_autoload_register(static function (string $classe): void {
    $prefixe = 'App\\';
    if (!str_starts_with($classe, $prefixe)) {
        return;
    }

    $relatif = substr($classe, strlen($prefixe));
    $fichier = __DIR__ . '/' . str_replace('\\', '/', $relatif) . '.php';

    if (is_file($fichier)) {
        require $fichier;
    }
});
