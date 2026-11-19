<?php
declare(strict_types=1);

use App\Controllers\AuthController;
use App\Controllers\DemandeController;
use App\Controllers\HealthController;
use App\Support\Request;
use App\Support\Response;
use App\Support\Router;

/**
 * Table des routes de l'API.
 * Toutes les réponses sont du JSON ; aucune page HTML n'est servie ici.
 */
$router = new Router();

/**
 * Un identifiant de demande doit être un entier positif écrit en chiffres.
 * « 1 OR 1=1 » ou « 12abc » ne sont pas convertis en entier : on répond 404
 * avant tout appel au dépôt (aucune requête SQL n'est construite).
 */
$identifiant = static function (array $parametres): ?int {
    $id = $parametres['id'] ?? null;

    if (!is_string($id) || !ctype_digit($id) || (int) $id <= 0) {
        return null;
    }

    return (int) $id;
};

$router->add(
    'GET',
    '/api/sante',
    static fn (array $parametres, Request $requete): Response => (new HealthController())->index()
);

$router->add(
    'POST',
    '/api/connexion',
    static fn (array $parametres, Request $requete): Response => (new AuthController())->connecter($requete)
);

$router->add(
    'POST',
    '/api/deconnexion',
    static fn (array $parametres, Request $requete): Response => (new AuthController())->deconnecter()
);

$router->add(
    'GET',
    '/api/moi',
    static fn (array $parametres, Request $requete): Response => (new AuthController())->moi()
);

$router->add(
    'GET',
    '/api/demandes',
    static fn (array $parametres, Request $requete): Response => (new DemandeController())->lister($requete)
);

$router->add(
    'GET',
    '/api/demandes/{id}',
    static function (array $parametres, Request $requete) use ($identifiant): Response {
        $id = $identifiant($parametres);

        if ($id === null) {
            return Response::erreur(404, 'DEMANDE_INCONNUE', 'Demande inconnue.');
        }

        return (new DemandeController())->detail($id, $requete);
    }
);

$router->add(
    'POST',
    '/api/demandes',
    static fn (array $parametres, Request $requete): Response => (new DemandeController())->creer($requete)
);

$router->add(
    'PATCH',
    '/api/demandes/{id}/statut',
    static function (array $parametres, Request $requete) use ($identifiant): Response {
        $id = $identifiant($parametres);

        if ($id === null) {
            return Response::erreur(404, 'DEMANDE_INCONNUE', 'Demande inconnue.');
        }

        return (new DemandeController())->changerStatut($id, $requete);
    }
);

return $router;
