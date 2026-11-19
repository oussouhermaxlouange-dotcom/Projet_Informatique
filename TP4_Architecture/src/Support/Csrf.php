<?php
declare(strict_types=1);

namespace App\Support;

/**
 * Défense CSRF.
 *
 * L'API est consommée en JSON par fetch depuis la même origine ; le cookie de
 * session est SameSite=Lax et le serveur n'active aucune CORS. On ajoute un
 * contrôle explicite de l'en-tête Origin : une requête d'écriture venue d'un
 * autre site est refusée (403) avant même d'atteindre le routeur.
 *
 * Un client sans navigateur (curl, scripts de test) n'envoie pas Origin : il
 * reste soumis à l'authentification par session, comme avant.
 */
final class Csrf
{
    private const METHODES_A_RISQUE = ['POST', 'PATCH', 'PUT', 'DELETE'];

    /**
     * @param array<string, mixed> $serveur superglobale $_SERVER
     */
    public static function verifier(Request $requete, array $serveur): void
    {
        if (!in_array(strtoupper($requete->methode), self::METHODES_A_RISQUE, true)) {
            return;
        }

        $origine = $serveur['HTTP_ORIGIN'] ?? '';

        if (!is_string($origine) || $origine === '') {
            return;
        }

        $hote = $serveur['HTTP_HOST'] ?? '';

        if (!is_string($hote) || !self::memeOrigine($origine, $hote)) {
            throw new ApiException(
                403,
                'ORIGINE_REFUSEE',
                'Requête refusée : cette origine n’est pas celle de l’application.'
            );
        }
    }

    /** Compare l'origine déclarée (schéma + hôte + port) à l'en-tête Host. */
    public static function memeOrigine(string $origine, string $hote): bool
    {
        $parties = parse_url($origine);

        if (!is_array($parties) || !isset($parties['host']) || !is_string($parties['host'])) {
            return false;
        }

        $autorite = $parties['host'];

        if (isset($parties['port']) && is_int($parties['port'])) {
            $autorite .= ':' . $parties['port'];
        }

        return hash_equals(strtolower($hote), strtolower($autorite));
    }
}
