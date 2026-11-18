<?php
declare(strict_types=1);

namespace App\Support;

use JsonException;

/**
 * Requête HTTP normalisée.
 * En production, elle est construite depuis les superglobales ; dans les tests,
 * on l'instancie directement, sans passer par un serveur.
 */
final class Request
{
    /**
     * @param array<string, mixed>  $corps
     * @param array<string, string> $query
     */
    public function __construct(
        public readonly string $methode,
        public readonly string $chemin,
        public readonly array $corps = [],
        public readonly array $query = [],
        public readonly bool $corpsInvalide = false
    ) {
    }

    public static function depuisGlobals(): self
    {
        $methode = strtoupper((string) ($_SERVER['REQUEST_METHOD'] ?? 'GET'));

        $chemin = parse_url((string) ($_SERVER['REQUEST_URI'] ?? '/'), PHP_URL_PATH);
        $chemin = is_string($chemin) && $chemin !== '' ? $chemin : '/';

        $brut = file_get_contents('php://input');
        $corps = [];
        $corpsInvalide = false;

        if (is_string($brut) && trim($brut) !== '') {
            try {
                $decode = json_decode($brut, true, 512, JSON_THROW_ON_ERROR);
                if (is_array($decode)) {
                    $corps = $decode;
                } else {
                    $corpsInvalide = true;
                }
            } catch (JsonException) {
                $corpsInvalide = true;
            }
        }

        $query = [];
        foreach ($_GET as $cle => $valeur) {
            if (is_string($cle) && is_string($valeur)) {
                $query[$cle] = $valeur;
            }
        }

        return new self($methode, $chemin, $corps, $query, $corpsInvalide);
    }

    /**
     * Corps JSON décodé, ou exception 400 si le corps n'est pas un objet JSON.
     *
     * @return array<string, mixed>
     */
    public function corpsValide(): array
    {
        if ($this->corpsInvalide) {
            throw new ApiException(
                400,
                'JSON_INVALIDE',
                'Le corps de la requête doit être un objet JSON valide.'
            );
        }

        return $this->corps;
    }
}
