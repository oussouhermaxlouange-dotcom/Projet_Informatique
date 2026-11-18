<?php
declare(strict_types=1);

/**
 * Produit l'empreinte bcrypt d'un mot de passe, à coller dans un INSERT
 * ou à utiliser pour remplacer un mot de passe de démonstration.
 *
 * Usage : php tools/hacher_mot_de_passe.php 'MotDePasse'
 */

$motDePasse = $argv[1] ?? null;

if (!is_string($motDePasse) || $motDePasse === '') {
    fwrite(STDERR, "Usage : php tools/hacher_mot_de_passe.php 'MotDePasse'\n");
    exit(1);
}

echo password_hash($motDePasse, PASSWORD_DEFAULT), PHP_EOL;
