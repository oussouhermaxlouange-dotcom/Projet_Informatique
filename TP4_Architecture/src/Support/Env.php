<?php
declare(strict_types=1);

namespace App\Support;

/**
 * Chargement minimal du fichier .env (aucune dépendance externe).
 * Les valeurs déjà présentes dans l'environnement ne sont pas écrasées.
 */
final class Env
{
    public static function load(string $fichier): void
    {
        if (!is_file($fichier)) {
            return;
        }

        $lignes = file($fichier, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if ($lignes === false) {
            return;
        }

        foreach ($lignes as $ligne) {
            $ligne = trim($ligne);
            if ($ligne === '' || str_starts_with($ligne, '#')) {
                continue;
            }

            $position = strpos($ligne, '=');
            if ($position === false) {
                continue;
            }

            $cle = trim(substr($ligne, 0, $position));
            $valeur = trim(substr($ligne, $position + 1));

            if ($cle === '') {
                continue;
            }

            if (strlen($valeur) >= 2) {
                $premier = $valeur[0];
                $dernier = $valeur[strlen($valeur) - 1];
                if (($premier === '"' && $dernier === '"') || ($premier === "'" && $dernier === "'")) {
                    $valeur = substr($valeur, 1, -1);
                }
            }

            if (getenv($cle) === false) {
                putenv($cle . '=' . $valeur);
                $_ENV[$cle] = $valeur;
                $_SERVER[$cle] = $valeur;
            }
        }
    }

    public static function get(string $cle, ?string $defaut = null): ?string
    {
        $valeur = $_ENV[$cle] ?? $_SERVER[$cle] ?? getenv($cle);

        if ($valeur === false || $valeur === null || $valeur === '') {
            return $defaut;
        }

        return (string) $valeur;
    }
}
